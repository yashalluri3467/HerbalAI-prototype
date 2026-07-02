# backend/utils/train_tf_models.py
"""Training utility for TensorFlow EfficientNetB0 models on the supported image datasets.

Usage:
    python -m backend.utils.train_tf_models --dataset <name> [--epochs N] [--batch-size N]

Supported dataset names are defined in `backend/utils/tf_preprocess.py` under `DATASET_SPECS`.
The script will download, prepare the dataset, train a lightweight EfficientNetB0 model (CPU only),
and save the trained model to `backend/models/<name>/model.h5`.
"""

import argparse
import pathlib
import tensorflow as tf
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.tf_preprocess import load_tf_dataset, DATASET_SPECS

def build_model(num_classes: int) -> tf.keras.Model:
    """Construct a simple EfficientNetB0 based classifier.
    
    We use `weights=None` to train from scratch (CPU‑friendly) and add a global average pooling
    layer followed by a dense softmax output.
    """
    base = tf.keras.applications.EfficientNetB0(
        include_top=False,
        weights=None,
        input_shape=(224, 224, 3),
    )
    x = tf.keras.layers.GlobalAveragePooling2D()(base.output)
    outputs = tf.keras.layers.Dense(num_classes, activation="softmax")(x)
    model = tf.keras.Model(inputs=base.input, outputs=outputs)
    model.compile(
        optimizer=tf.keras.optimizers.Adam(),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model

def train_dataset(name: str, epochs: int = 5, batch_size: int = 32):
    if name not in DATASET_SPECS:
        raise ValueError(f"Dataset '{name}' not recognized. Available: {list(DATASET_SPECS)}")

    # load_tf_dataset now returns (train_ds, val_ds, class_names)
    train_ds, val_ds, class_names = load_tf_dataset(name, batch_size=batch_size)
    num_classes = len(class_names)
    print(f"\nTraining '{name}' | classes={num_classes} | epochs={epochs} | batch={batch_size}")
    print("Classes:", class_names)

    model = build_model(num_classes)
    model.fit(train_ds, validation_data=val_ds, epochs=epochs)

    save_dir = pathlib.Path(__file__).resolve().parent.parent / "models" / name
    save_dir.mkdir(parents=True, exist_ok=True)
    model_path = save_dir / "model.keras"
    model.save(model_path)
    print(f"\nModel saved -> {model_path}")
    # Also save class labels for inference
    labels_path = save_dir / "class_names.txt"
    labels_path.write_text("\n".join(class_names))
    print(f"Class labels -> {labels_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train TensorFlow EfficientNetB0 on a selected dataset")
    parser.add_argument("--dataset", required=True, help="Dataset short name (e.g., mendeley, medicinal_leaves, isic, skin_disease)")
    parser.add_argument("--epochs", type=int, default=5, help="Number of training epochs (default 5)")
    parser.add_argument("--batch-size", type=int, default=32, help="Batch size for training (default 32)")
    args = parser.parse_args()
    train_dataset(args.dataset, epochs=args.epochs, batch_size=args.batch_size)
