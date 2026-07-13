# backend/utils/train_tf_models.py
"""Training utility for TensorFlow image classifiers on the supported datasets.

Usage:
    python -m utils.train_tf_models --dataset <name> [options]

Supported dataset names are defined in ``utils/tf_preprocess.DATASET_SPECS``.

This uses ImageNet transfer learning (a pretrained backbone with a fresh head) plus a
short fine-tune phase. The previous version trained EfficientNetB0 from scratch on CPU,
which collapsed to a near-constant output (the same class for every image). Transfer
learning + fine-tuning fixes that.

Tuning highlights
-----------------
* GPU is used automatically when present (all visible CUDA devices); falls back to CPU.
* Two-phase training: frozen backbone (head only) -> fine-tune top third of backbone.
* ``ModelCheckpoint`` keeps the best validation-accuracy weights globally across both phases.
* ``EarlyStopping`` and ``ReduceLROnPlateau`` curb over-fitting and recover from plateaus.
* Class weights correct for label imbalance (e.g. after merging heterogeneous sources).
* After training, a classification report + confusion matrix are written so every run is
  auditable (``skin_benchmark_report.md`` for the skin model).

For the skin model we train both MobileNetV2 and EfficientNetB0 and deploy the one with the
best validation macro-F1:

    python -m utils.train_tf_models --dataset skin_disease --train-both
"""

import argparse
import json
import logging
import pathlib
import sys
import os

import numpy as np
import tensorflow as tf

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.tf_preprocess import load_tf_dataset, DATASET_SPECS  # noqa: E402

logger = logging.getLogger("HerbalAI.Train")


# ---------------------------------------------------------------------------
# Device setup – use every CUDA core we can get, else CPU.
# ---------------------------------------------------------------------------
def configure_device():
    """Enable GPU memory growth and report the device. Returns ('GPU'|'CPU', count)."""
    gpus = tf.config.list_physical_devices("GPU")
    if gpus:
        try:
            for g in gpus:
                tf.config.experimental.set_memory_growth(g, True)
            logger.info(
                "GPU(s) available: %s – training on CUDA.", [g.name for g in gpus]
            )
            return "GPU", len(gpus)
        except (
            RuntimeError
        ) as exc:  # memory growth must be set before GPUs are initialised
            logger.warning(
                "Could not configure GPU memory growth (%s); continuing.", exc
            )
            return "GPU", len(gpus)
    logger.info("No GPU found – training on CPU.")
    return "CPU", 0


# ---------------------------------------------------------------------------
# Model construction
# ---------------------------------------------------------------------------
def build_backbone(backbone: str, weights, input_tensor):
    """Return a feature-extractor backbone (optionally ImageNet-pretrained).

    ``input_tensor`` must already be scaled to the range the backbone expects
    (MobileNetV2: [-1, 1]; EfficientNetB0: [0, 255] – it normalises internally).
    """
    if backbone == "efficientnetb0":
        return tf.keras.applications.EfficientNetB0(
            include_top=False, weights=weights, input_tensor=input_tensor
        )
    # default: MobileNetV2 – fastest on CPU, strong with ImageNet weights
    return tf.keras.applications.MobileNetV2(
        include_top=False, weights=weights, input_tensor=input_tensor
    )


def build_model(
    num_classes: int,
    weights: str = "imagenet",
    backbone: str = "mobilenetv2",
    img_size: int = 160,
):
    """Build the classifier with backbone-correct preprocessing baked in.

    The data pipeline (and the inference predictor) feed images scaled to [0, 1].
    The model converts that internally to each backbone's expected input range, so
    the ImageNet weights actually help instead of seeing mis-scaled pixels.
    """
    inputs = tf.keras.Input(shape=(img_size, img_size, 3))  # receives [0, 1]
    x255 = tf.keras.layers.Rescaling(255.0)(inputs)  # -> [0, 255]
    if backbone == "efficientnetb0":
        # Keras EfficientNetB0 bundles its own [0,255] -> normalised preprocessing.
        pre = x255
    else:
        # MobileNetV2 expects [-1, 1].
        pre = tf.keras.applications.mobilenet_v2.preprocess_input(x255)

    try:
        base = build_backbone(backbone, weights, pre)
    except (OSError, ValueError, FileNotFoundError) as exc:
        logger.critical(
            "Could not load ImageNet weights (%s). Falling back to weights=None. "
            "From-scratch training on many classes will be weak; ensure internet access "
            "so ~/.keras can cache ImageNet weights, or provide weights via IMAGENET_WEIGHTS_PATH.",
            exc,
        )
        base = build_backbone(backbone, None, pre)

    x = tf.keras.layers.GlobalAveragePooling2D()(base.output)
    x = tf.keras.layers.Dropout(0.25)(x)
    outputs = tf.keras.layers.Dense(num_classes, activation="softmax")(x)
    model = tf.keras.Model(inputs=inputs, outputs=outputs)
    return model, base


# ---------------------------------------------------------------------------
# Metrics (no sklearn dependency)
# ---------------------------------------------------------------------------
def compute_metrics(y_true, y_pred, class_names):
    """Return (per_class_dict, confusion_matrix, overall_dict)."""
    n = len(class_names)
    cm = np.zeros((n, n), dtype=int)
    for t, p in zip(y_true, y_pred):
        cm[int(t)][int(p)] += 1

    per_class = {}
    support_total = 0
    correct = 0
    for i in range(n):
        tp = int(cm[i, i])
        fp = int(cm[:, i].sum() - tp)
        fn = int(cm[i, :].sum() - tp)
        prec = tp / (tp + fp) if (tp + fp) else 0.0
        rec = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
        support = int(cm[i, :].sum())
        per_class[class_names[i]] = {
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1": round(f1, 4),
            "support": support,
        }
        support_total += support
        correct += tp

    macro_f1 = float(np.mean([per_class[c]["f1"] for c in class_names])) if n else 0.0
    weighted_f1 = (
        sum(per_class[c]["f1"] * per_class[c]["support"] for c in class_names)
        / support_total
        if support_total
        else 0.0
    )
    accuracy = correct / support_total if support_total else 0.0
    overall = {
        "accuracy": round(accuracy, 4),
        "macro_f1": round(macro_f1, 4),
        "weighted_f1": round(weighted_f1, 4),
    }
    return per_class, cm, overall


def _write_confusion_png(cm, class_names, out_path: pathlib.Path):
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(
            figsize=(max(8, len(class_names) * 0.5), max(6, len(class_names) * 0.45))
        )
        im = ax.imshow(cm, cmap="Blues")
        ax.set_xticks(range(len(class_names)))
        ax.set_yticks(range(len(class_names)))
        ax.set_xticklabels(class_names, rotation=90, fontsize=6)
        ax.set_yticklabels(class_names, fontsize=6)
        ax.set_xlabel("Predicted")
        ax.set_ylabel("True")
        ax.set_title("Confusion matrix (validation)")
        fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        fig.tight_layout()
        fig.savefig(out_path, dpi=150)
        plt.close(fig)
        return True
    except Exception as exc:  # pragma: no cover – plotting is best-effort
        logger.warning("Could not render confusion matrix PNG: %s", exc)
        return False


# ---------------------------------------------------------------------------
# Training
# ---------------------------------------------------------------------------
def train_dataset(
    name: str,
    epochs: int = 15,
    batch_size: int = 32,
    image_size: int = 160,
    backbone: str = "mobilenetv2",
    weights: str = "imagenet",
    finetune_epochs: int = 10,
    out_name: str = None,
    device: str = "CPU",
):
    if name not in DATASET_SPECS:
        raise ValueError(
            f"Dataset '{name}' not recognized. Available: {list(DATASET_SPECS)}"
        )
    out_name = out_name or name

    train_ds, val_ds, class_names = load_tf_dataset(
        name, batch_size=batch_size, img_size=(image_size, image_size)
    )
    num_classes = len(class_names)
    print(
        f"\nTraining '{name}' -> '{out_name}' | classes={num_classes} | epochs={epochs} | "
        f"batch={batch_size} | backbone={backbone} | weights={weights} | device={device}"
    )
    print("Classes:", class_names)

    # ---- class weights to offset imbalance ----
    counts = [0] * num_classes
    for _, y in train_ds:
        for v in y.numpy().flatten():
            counts[int(v)] += 1
    total = sum(counts) or 1
    class_weight = {
        i: (total / (num_classes * c)) if c > 0 else 1.0 for i, c in enumerate(counts)
    }
    logger.info("Class distribution: %s", dict(zip(class_names, counts)))

    model, base = build_model(
        num_classes, weights=weights, backbone=backbone, img_size=image_size
    )

    save_dir = pathlib.Path(__file__).resolve().parent.parent / "models" / out_name
    save_dir.mkdir(parents=True, exist_ok=True)
    ckpt_path = save_dir / "best_model.keras"

    checkpoint = tf.keras.callbacks.ModelCheckpoint(
        str(ckpt_path), monitor="val_accuracy", save_best_only=True, verbose=1
    )
    early_stop = tf.keras.callbacks.EarlyStopping(
        monitor="val_accuracy", patience=6, restore_best_weights=False, verbose=1
    )
    reduce_lr = tf.keras.callbacks.ReduceLROnPlateau(
        monitor="val_accuracy", factor=0.5, patience=3, min_lr=1e-7, verbose=1
    )
    callbacks = [checkpoint, early_stop, reduce_lr]

    # ---- Phase 1: train only the new head with the backbone frozen ----
    base.trainable = False
    model.compile(
        optimizer=tf.keras.optimizers.Adam(1e-3),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    print("\n[Phase 1] Training classification head (backbone frozen) ...")
    model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=epochs,
        class_weight=class_weight,
        callbacks=callbacks,
    )

    # ---- Phase 2: fine-tune the top third of the backbone at a low LR ----
    if finetune_epochs and finetune_epochs > 0:
        base.trainable = True
        unfreeze_from = max(1, len(base.layers) - len(base.layers) // 3)
        for layer in base.layers[:unfreeze_from]:
            layer.trainable = False
        model.compile(
            optimizer=tf.keras.optimizers.Adam(1e-5),
            loss="sparse_categorical_crossentropy",
            metrics=["accuracy"],
        )
        print("\n[Phase 2] Fine-tuning top layers of the backbone ...")
        model.fit(
            train_ds,
            validation_data=val_ds,
            epochs=finetune_epochs,
            class_weight=class_weight,
            callbacks=callbacks,
        )

    # ---- Load the globally-best weights and evaluate ----
    if ckpt_path.exists():
        logger.info("Loading best checkpoint: %s", ckpt_path)
        model = tf.keras.models.load_model(str(ckpt_path))

    y_true, y_pred = [], []
    for x, y in val_ds:
        preds = model.predict(x, verbose=0)
        y_true.extend(y.numpy().flatten().tolist())
        y_pred.extend(np.argmax(preds, axis=1).tolist())

    per_class, cm, overall = compute_metrics(y_true, y_pred, class_names)

    # ---- Persist model + labels ----
    model_path = save_dir / "model.keras"
    model.save(model_path)
    (save_dir / "class_names.txt").write_text("\n".join(class_names))
    print(f"\nModel saved -> {model_path}")

    # ---- Write metrics + report ----
    metrics = {
        "dataset": name,
        "out_name": out_name,
        "backbone": backbone,
        "image_size": image_size,
        "device": device,
        "num_classes": num_classes,
        "total_params": int(model.count_params()),
        "accuracy": overall["accuracy"],
        "macro_f1": overall["macro_f1"],
        "weighted_f1": overall["weighted_f1"],
    }
    (save_dir / "metrics.json").write_text(json.dumps(metrics, indent=2))

    png_ok = _write_confusion_png(cm, class_names, save_dir / "confusion_matrix.png")
    _write_report_md(
        name,
        out_name,
        backbone,
        image_size,
        device,
        overall,
        per_class,
        cm,
        save_dir / "benchmark_report.md",
        png_ok,
    )

    print(
        f"\nValidation accuracy: {overall['accuracy']:.4f} | "
        f"macro-F1: {overall['macro_f1']:.4f} | weighted-F1: {overall['weighted_f1']:.4f}"
    )
    return metrics


def _write_report_md(
    name,
    out_name,
    backbone,
    image_size,
    device,
    overall,
    per_class,
    cm,
    out_path: pathlib.Path,
    png_ok: bool,
):
    lines = [
        f"# Training benchmark — `{out_name}`",
        "",
        f"- Dataset: `{name}`",
        f"- Backbone: `{backbone}` (input {image_size}x{image_size})",
        f"- Device: {device}",
        f"- Accuracy: **{overall['accuracy']:.4f}**",
        f"- Macro-F1: **{overall['macro_f1']:.4f}**",
        f"- Weighted-F1: {overall['weighted_f1']:.4f}",
        "",
        "## Per-class metrics",
        "",
        "| Class | Precision | Recall | F1 | Support |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for c, m in per_class.items():
        lines.append(
            f"| {c} | {m['precision']:.3f} | {m['recall']:.3f} | {m['f1']:.3f} | {m['support']} |"
        )
    lines += ["", "## Confusion matrix", ""]
    if png_ok:
        lines.append(
            f"![confusion matrix]({out_path.parent.name}/confusion_matrix.png)"
        )
        lines.append("")
    header = " | ".join([""] + list(per_class.keys()) + [""])
    lines.append(header)
    for c, m in per_class.items():
        row = [c] + [
            str(cm[i, list(per_class).index(c)]) for i in range(len(per_class))
        ]
        lines.append(" | ".join([""] + row + [""]))
    lines.append("")
    out_path.write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# Train both backbones and deploy the best (skin model workflow)
# ---------------------------------------------------------------------------
def train_both(
    name: str,
    epochs: int = 15,
    batch_size: int = 32,
    image_size: int = 224,
    weights: str = "imagenet",
    finetune_epochs: int = 10,
    device: str = "CPU",
):
    models_root = pathlib.Path(__file__).resolve().parent.parent / "models"
    live_dir = models_root / name
    results = {}
    for backbone in ("mobilenetv2", "efficientnetb0"):
        out_name = f"{name}_{backbone}"
        metrics = train_dataset(
            name,
            epochs=epochs,
            batch_size=batch_size,
            image_size=image_size,
            backbone=backbone,
            weights=weights,
            finetune_epochs=finetune_epochs,
            out_name=out_name,
            device=device,
        )
        results[backbone] = metrics

    best = max(results, key=lambda b: results[b]["macro_f1"])
    logger.info(
        "Best backbone by validation macro-F1: %s (%.4f) vs %s (%.4f)",
        best,
        results[best]["macro_f1"],
        [b for b in results if b != best][0],
        results[[b for b in results if b != best][0]]["macro_f1"],
    )

    src = models_root / f"{name}_{best}"
    for fname in (
        "model.keras",
        "class_names.txt",
        "metrics.json",
        "benchmark_report.md",
        "confusion_matrix.png",
    ):
        s = src / fname
        if s.exists():
            shutil_copy = __import__("shutil").copy2
            shutil_copy(s, live_dir / fname)
    logger.info("Deployed best model -> %s", live_dir / "model.keras")

    # Aggregate comparison report at the live model location.
    comparison = {"selected_backbone": best, "candidates": results}
    (live_dir / "selection.json").write_text(json.dumps(comparison, indent=2))
    _write_skin_summary(name, live_dir, results, best)


def _write_skin_summary(name, live_dir, results, best):
    lines = [
        f"# Skin model (`{name}`) — backbone selection",
        "",
        f"Selected backbone: **{best}** (best validation macro-F1).",
        "",
        "| Backbone | Accuracy | Macro-F1 | Weighted-F1 | Params | Device |",
        "| --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for b, m in results.items():
        lines.append(
            f"| {b} | {m['accuracy']:.4f} | {m['macro_f1']:.4f} | "
            f"{m['weighted_f1']:.4f} | {m['total_params']:,} | {m['device']} |"
        )
    lines.append("")
    lines.append(
        f"The winner was copied to `models/{name}/` and is served by "
        "`POST /api/predict/skin`."
    )
    lines.append("")
    (live_dir.parent.parent / "skin_benchmark_report.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )
    logger.info("Wrote skin_benchmark_report.md")


if __name__ == "__main__":
    device, _ = configure_device()
    parser = argparse.ArgumentParser(
        description="Train a TensorFlow image classifier on a selected dataset"
    )
    parser.add_argument(
        "--dataset",
        required=True,
        help="Dataset short name (e.g., mendeley, medicinal_leaves, isic, skin_disease)",
    )
    parser.add_argument(
        "--epochs", type=int, default=15, help="Phase-1 epochs (default 15)"
    )
    parser.add_argument(
        "--batch-size", type=int, default=32, help="Batch size (default 32)"
    )
    parser.add_argument(
        "--image-size", type=int, default=160, help="Input image size (default 160)"
    )
    parser.add_argument(
        "--backbone",
        choices=["mobilenetv2", "efficientnetb0"],
        default="mobilenetv2",
        help="Backbone architecture (default mobilenetv2)",
    )
    parser.add_argument(
        "--weights",
        choices=["imagenet", "none"],
        default="imagenet",
        help="Backbone weights (default imagenet)",
    )
    parser.add_argument(
        "--finetune-epochs",
        type=int,
        default=10,
        help="Phase-2 fine-tune epochs (default 10)",
    )
    parser.add_argument(
        "--out-name",
        default=None,
        help="Override the model output directory name (default: same as --dataset)",
    )
    parser.add_argument(
        "--train-both",
        action="store_true",
        help="Train both MobileNetV2 and EfficientNetB0, deploy the best by val macro-F1 "
        "(used for the skin_disease model)",
    )
    args = parser.parse_args()

    if args.train_both:
        train_both(
            args.dataset,
            epochs=args.epochs,
            batch_size=args.batch_size,
            image_size=args.image_size,
            weights=args.weights,
            finetune_epochs=args.finetune_epochs,
            device=device,
        )
    else:
        train_dataset(
            args.dataset,
            epochs=args.epochs,
            batch_size=args.batch_size,
            image_size=args.image_size,
            backbone=args.backbone,
            weights=args.weights,
            finetune_epochs=args.finetune_epochs,
            out_name=args.out_name,
            device=device,
        )
