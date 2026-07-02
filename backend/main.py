import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

import io
import base64
import logging
import torch
import cv2
import numpy as np
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

# Import our custom modules
from database.knowledge_base import get_all_herbs, get_herb_by_name
from models.classifiers import SkinConditionClassifier, HerbClassifier
from models.gradcam import GradCAM
from utils.prep import preprocess_image_pipeline
import tensorflow as tf
from pathlib import Path
from services.recommender import RecommenderService
from services.explainer import ExplainerService
from services.tf_predictor import predict as tf_predict, available_datasets as tf_available
import services.llm_service as llm_service
from starlette.concurrency import run_in_threadpool

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("HerbalAI")

# Auto-train models if weights are missing
backend_dir = Path(__file__).resolve().parent
weights_exist = (backend_dir / "weights" / "skin_model.pth").exists() and (backend_dir / "weights" / "herb_model.pth").exists()
if not weights_exist:
    logger.info("Weights not found. Running synthetic dataset pre-training pipeline...")
    # Import and run the pre-training script inline
    import subprocess
    import sys
    # Run setup_models.py in the current environment
    try:
        setup_script = backend_dir / "utils" / "setup_models.py"
        subprocess.check_call([sys.executable, str(setup_script)], cwd=str(backend_dir))
    except Exception as e:
        logger.error(f"Failed to auto-train synthetic models: {e}")

# Initialize FastAPI app
app = FastAPI(
    title="Ayurvedic Skin Diagnosis & Herbal Recommendation System API",
    description="Full-stack AI healthcare engine combining Computer Vision + Knowledge Base + Grad-CAM Explainable AI",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define label sets
SKIN_CLASSES = ["Acne", "Eczema", "Pigmentation", "Dry Skin", "Wrinkles", "Psoriasis", "Rosacea", "Healthy Skin"]
HERB_CLASSES = [
    "Neem", "Aloe Vera", "Turmeric", "Tulsi", "Amla", 
    "Harra", "Bahera", "Giloy", "Mahua", "Karanj", 
    "Palash", "Moringa", "Hibiscus", "Ashwagandha", 
    "Bael", "Arjun", "Chironji", "Bhringraj"
]

# Dynamically load herb classes if the custom training script has generated herb_classes.txt
herb_classes_file = Path(__file__).resolve().parent / "models" / "herb_classes.txt"
if herb_classes_file.exists():
    try:
        with open(herb_classes_file, "r", encoding="utf-8") as f:
            loaded_classes = [line.strip() for line in f if line.strip()]
            if loaded_classes:
                HERB_CLASSES = loaded_classes
                logger.info(f"Loaded {len(HERB_CLASSES)} custom herb classes from {herb_classes_file}")
    except Exception as e:
        logger.error(f"Error loading custom herb classes: {e}")

# Load Models
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
logger.info(f"Using device: {device}")
# Resolve paths to weights relative to backend directory
weights_dir = Path(__file__).resolve().parent / "weights"
skin_model_path = weights_dir / "skin_model.pth"
herb_model_path = weights_dir / "herb_model.pth"

skin_model = SkinConditionClassifier(num_classes=len(SKIN_CLASSES), use_pretrained=False)
if skin_model_path.exists():
    skin_model.load_state_dict(torch.load(skin_model_path, map_location=device))
skin_model.to(device)
skin_model.eval()

herb_model = HerbClassifier(num_classes=len(HERB_CLASSES), use_pretrained=False)
if herb_model_path.exists():
    herb_model.load_state_dict(torch.load(herb_model_path, map_location=device))
herb_model.to(device)
herb_model.eval()
def image_to_base64(img_bgr):
    """Converts a BGR image to a base64 string"""
    _, buffer = cv2.imencode('.jpg', img_bgr)
    b64_str = base64.b64encode(buffer).decode('utf-8')
    return f"data:image/jpeg;base64,{b64_str}"

@app.get("/")
def read_root():
    return {
        "status": "online",
        "message": "Ayurvedic Skin Diagnosis API is active",
        "classes": {
            "skin_diseases": SKIN_CLASSES,
            "herbs": HERB_CLASSES
        }
    }

@app.get("/api/herbs")
def get_herbs():
    return get_all_herbs()

@app.get("/api/herbs/{name}")
def get_herb(name: str):
    herb = get_herb_by_name(name)
    if not herb:
        raise HTTPException(status_code=404, detail=f"Herb '{name}' not found")
    return herb

@app.post("/api/predict/skin")
async def predict_skin(file: UploadFile = File(...)):
    """
    Classifies skin disease, runs Grad-CAM, and recommends suitable herbs.
    """
    try:
        contents = await file.read()
        
        # Preprocess
        input_tensor, bgr_original, bgr_enhanced = preprocess_image_pipeline(contents)
        input_tensor = input_tensor.to(device)
        
        # Grad-CAM target layer: last convolution layer
        target_layer = skin_model.get_last_conv_layer()
        cam = GradCAM(skin_model, target_layer)
        
        # Inference & Heatmap Generation
        heatmap, class_idx = cam.generate_heatmap(input_tensor)
        predicted_disease = SKIN_CLASSES[class_idx]
        
        # Get raw logit confidence
        with torch.no_grad():
            logits = skin_model(input_tensor)
            probs = torch.softmax(logits, dim=1).cpu().numpy()[0]
            confidence = float(probs[class_idx])
            
        # Draw Grad-CAM overlay
        overlay = cam.overlay_heatmap(heatmap, bgr_original, alpha=0.45)
        cam.remove_hooks()
        
        # Base64 original needs to be ready for LLM fallback
        base64_original = image_to_base64(bgr_original)
        
        fallback_used = False
        if confidence < 0.39:
            logger.info("Low confidence in skin model. Using LLM fallback.")
            fallback_disease = await run_in_threadpool(llm_service.fallback_image_classification, base64_original, "skin")
            if fallback_disease and fallback_disease != "Unknown":
                # Validate: only accept if it matches a known class (case-insensitive)
                matched = next((c for c in SKIN_CLASSES if c.lower() == fallback_disease.strip().lower()), None)
                if matched:
                    predicted_disease = matched
                    fallback_used = True
                    logger.info(f"LLM fallback classified disease as: {predicted_disease}")
                else:
                    logger.warning(f"LLM fallback returned unrecognized class: '{fallback_disease}'. Keeping local model prediction.")

        # Get herbal recommendations (local model + knowledge base)
        rec_results = RecommenderService.recommend(predicted_disease, confidence)
        
        # Inject LOCAL explanations only (from ExplainerService, no LLM here)
        top_recs_with_explanations = []
        herb_names = []
        for rec in rec_results["top_recommendations"]:
            explanation = ExplainerService.generate_explanation(predicted_disease, rec["name"])
            herb_names.append(rec["name"])
            top_recs_with_explanations.append({
                **rec,
                "explanation": explanation
            })
        
        # Single LLM summary call (supplementary, shown at bottom of UI)
        llm_summary = await run_in_threadpool(llm_service.generate_diagnosis_summary, predicted_disease, herb_names)
            
        # Base64 encodings (enhanced and heatmap)
        base64_enhanced = image_to_base64(bgr_enhanced)
        base64_heatmap = image_to_base64(overlay)
        
        return {
            "disease": predicted_disease,
            "confidence_score": confidence,
            "original_image": base64_original,
            "enhanced_image": base64_enhanced,
            "gradcam_heatmap": base64_heatmap,
            "recommendations": top_recs_with_explanations,
            "llm_fallback_used": fallback_used,
            "llm_summary": llm_summary
        }
    except Exception as e:
        logger.error(f"Error during skin prediction: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/predict/leaf")
async def predict_leaf(file: UploadFile = File(...)):
    """
    Classifies herb leaf, runs Grad-CAM, and returns active compounds & details.
    """
    try:
        contents = await file.read()
        
        # Preprocess
        input_tensor, bgr_original, bgr_enhanced = preprocess_image_pipeline(contents)
        input_tensor = input_tensor.to(device)
        
        # Grad-CAM target layer
        target_layer = herb_model.get_last_conv_layer()
        cam = GradCAM(herb_model, target_layer)
        
        # Inference & Heatmap Generation
        heatmap, class_idx = cam.generate_heatmap(input_tensor)
        predicted_herb = HERB_CLASSES[class_idx]
        
        # Get raw logit confidence
        with torch.no_grad():
            logits = herb_model(input_tensor)
            probs = torch.softmax(logits, dim=1).cpu().numpy()[0]
            confidence = float(probs[class_idx])
            
        # Draw Grad-CAM overlay
        overlay = cam.overlay_heatmap(heatmap, bgr_original, alpha=0.45)
        cam.remove_hooks()
        
        base64_original = image_to_base64(bgr_original)
        
        fallback_used = False
        if confidence < 0.39:
            logger.info("Low confidence in herb model. Using LLM fallback.")
            fallback_herb = await run_in_threadpool(llm_service.fallback_image_classification, base64_original, "leaf")
            if fallback_herb and fallback_herb != "Unknown":
                # Validate: only accept if it matches a known class (case-insensitive)
                matched = next((c for c in HERB_CLASSES if c.lower() == fallback_herb.strip().lower()), None)
                if matched:
                    predicted_herb = matched
                    fallback_used = True
                    logger.info(f"LLM fallback classified leaf as: {predicted_herb}")
                else:
                    logger.warning(f"LLM fallback returned unrecognized herb: '{fallback_herb}'. Keeping local model prediction.")

        # Query details from knowledge base (local, no LLM)
        herb_details = get_herb_by_name(predicted_herb)
        
        # Single LLM summary call (supplementary, shown at bottom of UI)
        llm_summary = await run_in_threadpool(llm_service.generate_leaf_summary, predicted_herb)
        
        # Base64 encodings
        base64_enhanced = image_to_base64(bgr_enhanced)
        base64_heatmap = image_to_base64(overlay)
        
        return {
            "herb": predicted_herb,
            "confidence_score": confidence,
            "original_image": base64_original,
            "enhanced_image": base64_enhanced,
            "gradcam_heatmap": base64_heatmap,
            "details": herb_details,
            "llm_fallback_used": fallback_used,
            "llm_summary": llm_summary
        }
    except Exception as e:
        logger.error(f"Error during leaf prediction: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/predict/joint")
async def predict_joint(
    skin_file: UploadFile = File(...), 
    leaf_file: UploadFile = File(...)
):
    """
    Joint evaluation: Evaluates suitability of the uploaded leaf image 
    for the disease detected in the uploaded skin image.
    """
    try:
        # 1. Process skin image
        skin_contents = await skin_file.read()
        skin_tensor, skin_bgr, skin_bgr_enhanced = preprocess_image_pipeline(skin_contents)
        skin_tensor = skin_tensor.to(device)
        
        skin_target_layer = skin_model.get_last_conv_layer()
        skin_cam = GradCAM(skin_model, skin_target_layer)
        skin_heatmap, skin_class_idx = skin_cam.generate_heatmap(skin_tensor)
        predicted_disease = SKIN_CLASSES[skin_class_idx]
        
        with torch.no_grad():
            skin_logits = skin_model(skin_tensor)
            skin_probs = torch.softmax(skin_logits, dim=1).cpu().numpy()[0]
            skin_confidence = float(skin_probs[skin_class_idx])
            
        skin_overlay = skin_cam.overlay_heatmap(skin_heatmap, skin_bgr, alpha=0.45)
        skin_cam.remove_hooks()
        
        # 2. Process leaf image
        leaf_contents = await leaf_file.read()
        leaf_tensor, leaf_bgr, leaf_bgr_enhanced = preprocess_image_pipeline(leaf_contents)
        leaf_tensor = leaf_tensor.to(device)
        
        leaf_target_layer = herb_model.get_last_conv_layer()
        leaf_cam = GradCAM(herb_model, leaf_target_layer)
        leaf_heatmap, leaf_class_idx = leaf_cam.generate_heatmap(leaf_tensor)
        predicted_herb = HERB_CLASSES[leaf_class_idx]
        
        with torch.no_grad():
            leaf_logits = herb_model(leaf_tensor)
            leaf_probs = torch.softmax(leaf_logits, dim=1).cpu().numpy()[0]
            leaf_confidence = float(leaf_probs[leaf_class_idx])
            
        leaf_overlay = leaf_cam.overlay_heatmap(leaf_heatmap, leaf_bgr, alpha=0.45)
        leaf_cam.remove_hooks()
        
        # 3. Evaluate compatibility
        rec_results = RecommenderService.recommend(
            predicted_disease, 
            skin_confidence, 
            classified_herb=predicted_herb, 
            herb_confidence=leaf_confidence
        )
        
        evaluation = rec_results["leaf_evaluation"]
        explanation = ExplainerService.generate_explanation(predicted_disease, predicted_herb)
        
        # 4. Encodings
        skin_original_b64 = image_to_base64(skin_bgr)
        skin_heatmap_b64 = image_to_base64(skin_overlay)
        leaf_original_b64 = image_to_base64(leaf_bgr)
        leaf_heatmap_b64 = image_to_base64(leaf_overlay)
        
        return {
            "disease": predicted_disease,
            "disease_confidence": skin_confidence,
            "skin_original": skin_original_b64,
            "skin_heatmap": skin_heatmap_b64,
            
            "herb": predicted_herb,
            "herb_confidence": leaf_confidence,
            "leaf_original": leaf_original_b64,
            "leaf_heatmap": leaf_heatmap_b64,
            
            "evaluation": evaluation,
            "explanation": explanation
        }
    except Exception as e:
        logger.error(f"Error during joint prediction: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# TensorFlow / Keras model endpoints
# ---------------------------------------------------------------------------

@app.get("/api/tf/datasets")
def tf_datasets():
    """List all dataset names for which a trained TF model exists."""
    datasets = tf_available()
    return {"available_datasets": datasets}


@app.post("/api/tf/predict/{dataset_name}")
async def tf_predict_endpoint(dataset_name: str, file: UploadFile = File(...)):
    """
    Run TF/Keras inference on an uploaded image using the model trained
    on the specified dataset (e.g. medicinal_leaves, skin_disease).

    Returns top-1 prediction, confidence, and full probability distribution.
    """
    try:
        image_bytes = await file.read()
        result = tf_predict(dataset_name, image_bytes)
        return {
            "dataset": dataset_name,
            "predicted_class": result["predicted_class"],
            "confidence": result["confidence"],
            "all_probabilities": result["all_probs"],
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"TF predict error [{dataset_name}]: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


