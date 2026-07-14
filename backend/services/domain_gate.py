# backend/services/domain_gate.py
"""Domain-validation gate for upload validation.

Before running the skin / leaf diagnosis models, we verify that the uploaded
image actually depicts the expected domain (skin for the skin endpoint, leaf for
the leaf endpoint). This prevents the diagnosis models from returning a
confident-but-meaningless result for an off-domain image (a dog, a landscape, a
screenshot, ...).

The gate is a 3-class MobileNetV2 classifier (skin / leaf / other) trained by
`utils.train_tf_models --dataset domain_gate`. It lives at
`backend/models/domain_gate/`.

Graceful degradation: if the gate model has not been trained / deployed, every
check returns ``True`` (i.e. the validation is skipped) so the rest of the app
keeps working. A warning is logged once.
"""

import logging
import pathlib

import numpy as np
import tensorflow as tf

logger = logging.getLogger("HerbalAI.DomainGate")

# Probability the expected domain class must reach to be accepted.
GATE_THRESHOLD = 0.60

_MODELS_DIR = pathlib.Path(__file__).resolve().parent.parent / "models" / "domain_gate"

# Cache: (model, class_names, input_size) or None when the model is absent.
_cache = None
_warned_missing = False


def _load():
    global _cache, _warned_missing
    if _cache is not None or _warned_missing:
        return _cache

    model_path = _MODELS_DIR / "model.keras"
    labels_path = _MODELS_DIR / "class_names.txt"

    if not model_path.is_file():
        # Fall back to the best-validation checkpoint written during training, so a
        # run interrupted before the final save is still usable.
        best = _MODELS_DIR / "best_model.keras"
        if best.is_file():
            model_path = best
            logger.info("Domain-gate model.keras absent; using best_model.keras.")
        else:
            _warned_missing = True
            logger.warning(
                "Domain-gate model not found at %s — upload domain validation is "
                "DISABLED. Train it with: "
                "python -m utils.prepare_domain_gate && "
                "python -m utils.train_tf_models --dataset domain_gate --image-size 224",
                _MODELS_DIR,
            )
            return None

    model = tf.keras.models.load_model(model_path)
    class_names = (
        labels_path.read_text().strip().splitlines() if labels_path.is_file() else []
    )

    input_size = (224, 224)
    try:
        shape = model.inputs[0].shape
        if shape[1] is not None and shape[2] is not None:
            input_size = (int(shape[1]), int(shape[2]))
    except (AttributeError, IndexError, TypeError):
        pass

    _cache = (model, class_names, input_size)
    logger.info(
        "Domain-gate model loaded (classes=%s, size=%s)", class_names, input_size
    )
    return _cache


def _predict_probs(model, image_bytes: bytes, input_size: tuple) -> np.ndarray:
    img = tf.image.decode_image(image_bytes, channels=3, expand_animations=False)
    img = tf.image.resize(img, input_size)
    img = tf.cast(img, tf.float32) / 255.0
    img = tf.expand_dims(img, 0)
    return model.predict(img, verbose=0)[0]


def is_valid_domain(
    expected: str, image_bytes: bytes, threshold: float = GATE_THRESHOLD
) -> bool:
    """Return True if ``image_bytes`` depicts the ``expected`` domain.

    ``expected`` is one of ``"skin"`` / ``"leaf"``. The check passes when the
    expected class is the argmax *and* its softmax probability >= ``threshold``.

    Returns True (skip) when the gate model is absent, and True on any decode
    failure so a malformed upload falls through to the normal error handling.
    """
    loaded = _load()
    if loaded is None:
        return True  # gate not deployed -> don't block

    model, class_names, input_size = loaded
    if expected not in class_names:
        logger.warning(
            "Expected domain %r not in gate classes %s — skipping validation.",
            expected,
            class_names,
        )
        return True

    try:
        probs = _predict_probs(model, image_bytes, input_size)
    except Exception as exc:  # malformed image etc. -> let downstream handle it
        logger.warning("Domain-gate decode failed (%s); skipping validation.", exc)
        return True

    expected_idx = class_names.index(expected)
    predicted_idx = int(np.argmax(probs))
    expected_prob = float(probs[expected_idx])

    if predicted_idx == expected_idx and expected_prob >= threshold:
        return True

    logger.info(
        "Domain-gate rejected upload for '%s' (predicted=%s p=%.3f, %s p=%.3f)",
        expected,
        class_names[predicted_idx] if class_names else predicted_idx,
        float(probs[predicted_idx]) if class_names else 0.0,
        expected,
        expected_prob,
    )
    return False
