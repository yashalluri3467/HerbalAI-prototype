# backend/services/tf_predictor.py
"""Inference service for TF/Keras models saved by train_tf_models.py.

Each model lives at:
    backend/models/<dataset_name>/model.keras
    backend/models/<dataset_name>/class_names.txt

Models are loaded lazily on first use and cached in memory.
"""

import pathlib
import functools
import numpy as np
import tensorflow as tf

_MODELS_DIR = pathlib.Path(__file__).resolve().parent.parent / "models"

# Cache: dataset_name → (model, class_names)
_cache: dict = {}


def _load(name: str):
    if name in _cache:
        return _cache[name]

    model_path = _MODELS_DIR / name / "model.keras"
    labels_path = _MODELS_DIR / name / "class_names.txt"

    if not model_path.is_file():
        raise FileNotFoundError(
            f"No trained model found for '{name}'. "
            f"Expected: {model_path}\n"
            "Run  python utils/train_tf_models.py --dataset <name>  first."
        )

    model = tf.keras.models.load_model(model_path)
    class_names = labels_path.read_text().strip().splitlines() if labels_path.is_file() else []
    _cache[name] = (model, class_names)
    return model, class_names


def predict(name: str, image_bytes: bytes, img_size: tuple = (224, 224)) -> dict:
    """Run inference on raw image bytes.

    Returns
    -------
    dict with keys:
        predicted_class  – top-1 class label (str)
        confidence       – probability of top-1 class (float 0-1)
        all_probs        – {class_label: probability} for every class
    """
    model, class_names = _load(name)

    # Decode & preprocess
    img = tf.image.decode_image(image_bytes, channels=3, expand_animations=False)
    img = tf.image.resize(img, img_size)
    img = tf.cast(img, tf.float32) / 255.0
    img = tf.expand_dims(img, 0)   # (1, H, W, 3)

    probs = model.predict(img, verbose=0)[0]   # shape (num_classes,)
    top_idx = int(np.argmax(probs))

    predicted_class = class_names[top_idx] if class_names else str(top_idx)
    confidence = float(probs[top_idx])
    all_probs = {
        (class_names[i] if class_names else str(i)): float(probs[i])
        for i in range(len(probs))
    }

    return {
        "predicted_class": predicted_class,
        "confidence": round(confidence, 4),
        "all_probs": {k: round(v, 4) for k, v in sorted(all_probs.items(), key=lambda x: -x[1])},
    }


def available_datasets() -> list[str]:
    """Return dataset names that have a trained model ready."""
    result = []
    if _MODELS_DIR.is_dir():
        for d in _MODELS_DIR.iterdir():
            if d.is_dir() and (d / "model.keras").is_file():
                result.append(d.name)
    return sorted(result)
