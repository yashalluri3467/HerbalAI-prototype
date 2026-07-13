import os
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VerifyBackend")


def verify():
    logger.info("Starting verification of HerbalAI backend components...")

    # 1. Check core dependencies
    try:
        import fastapi  # noqa: F401
        import uvicorn  # noqa: F401
        import cv2  # noqa: F401
        import numpy as np  # noqa: F401

        logger.info("Successfully imported all core third-party dependencies.")
    except ImportError as e:
        logger.error(f"Dependency import failed: {e}")
        sys.exit(1)

    # 2. Check local modules (live TensorFlow stack only)
    try:
        from database.knowledge_base import get_all_herbs  # noqa: F401
        from services.recommender import RecommenderService  # noqa: F401
        from services.tf_predictor import predict as tf_predict  # noqa: F401

        logger.info("Successfully imported all local HerbalAI modules.")
    except ImportError as e:
        logger.error(f"Local module import failed: {e}")
        sys.exit(1)

    # 3. Check knowledge base contents
    herbs = get_all_herbs()
    logger.info(f"Herbal Knowledge Base loaded with {len(herbs)} herbs.")
    if len(herbs) != 18:
        logger.warning(
            f"Expected 18 herbs, found {len(herbs)}. Please double check database content."
        )

    # 4. Check trained model weights (live TF models)
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    leaf_model = os.path.join(backend_dir, "models", "medicinal_leaves", "model.keras")
    skin_model = os.path.join(backend_dir, "models", "skin_disease", "model.keras")
    if os.path.exists(leaf_model) and os.path.exists(skin_model):
        logger.info(
            "Trained TensorFlow model weights detected (medicinal_leaves, skin_disease)."
        )
    else:
        missing = [p for p in (leaf_model, skin_model) if not os.path.exists(p)]
        logger.warning(
            "Model weights not found: %s. Train with "
            "utils/train_tf_models.py --dataset <name>.",
            missing,
        )

    logger.info("Backend verification completed successfully!")


if __name__ == "__main__":
    verify()
