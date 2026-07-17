import base64
import logging
import os
from contextlib import asynccontextmanager
from typing import Optional

import cv2
import numpy as np
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import desc, select
from starlette.concurrency import run_in_threadpool

from database.db import DB_ENABLED, get_db, init_db, SessionLocal
from database.models import SessionRecord
from database.knowledge_base import get_all_herbs, get_herb_by_name
from services.recommender import RecommenderService
from services.tf_predictor import available_datasets as tf_available
from services.tf_predictor import predict as tf_predict
from services.domain_gate import is_valid_domain
import services.llm_service as llm_service

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("HerbalAI")


@asynccontextmanager
async def lifespan(app: FastAPI):
    if DB_ENABLED:
        await init_db()
        logger.info("Session-history database initialized")
    else:
        logger.warning("DATABASE_URL not set - session history will NOT be persisted")

    # Warm the in-memory model cache so the first prediction after a
    # deploy is not delayed by lazy model loading. Failures are logged
    # and never fatal. Disable with WARM_UP_MODELS=false.
    if os.getenv("WARM_UP_MODELS", "true").lower() != "false":
        try:
            from services import tf_predictor

            for _name in tf_predictor.available_datasets():
                try:
                    tf_predictor._load(_name)
                    logger.info("Warmed model: %s", _name)
                except Exception as exc:  # pragma: no cover
                    logger.warning("Could not warm model %s: %s", _name, exc)
        except Exception as exc:  # pragma: no cover
            logger.warning("Model warm-up skipped: %s", exc)

    yield


app = FastAPI(
    title="Ayurvedic Skin Diagnosis & Herbal Recommendation System API",
    description="Dataset-trained image classification with optional knowledge-base and LLM support",
    version="2.0.0",
    lifespan=lifespan,
)


async def _persist_session(
    session_type: str,
    response: dict,
    image: Optional[str] = None,
    dataset: Optional[str] = None,
) -> None:
    """Best-effort persistence of a prediction as a session record.

    Failures are logged and swallowed so a DB issue never breaks a prediction.
    """
    if not DB_ENABLED or SessionLocal is None:
        return
    try:
        predicted_class = (
            response.get("disease")
            or response.get("herb")
            or response.get("predicted_class")
        )
        confidence = (
            response.get("confidence_score")
            or response.get("confidence")
            or response.get("disease_confidence")
        )
        status = response.get("classification_status") or response.get(
            "leaf_classification_status"
        )
        async with SessionLocal() as db:
            db.add(
                SessionRecord(
                    session_type=session_type,
                    dataset=dataset,
                    predicted_class=predicted_class,
                    confidence=confidence,
                    status=status,
                    top_predictions=response.get("top_predictions")
                    or response.get("all_probabilities"),
                    recommendations=response.get("recommendations"),
                    llm_summary=response.get("llm_summary"),
                    image=image,
                    meta=response,
                )
            )
            await db.commit()
    except Exception as exc:  # pragma: no cover - persistence must never break API
        logger.warning("Failed to persist session record: %s", exc)


# Allowed CORS origins for the frontend. Defaults to "*" (any origin) when
# FRONTEND_URL is unset so local/dev and the Vercel frontend both work. Set
# FRONTEND_URL on Render (comma-separated) to restrict to specific origins.
_frontend_urls = os.getenv("FRONTEND_URL", "").strip()
allow_origins = (
    [u.strip() for u in _frontend_urls.split(",") if u.strip()]
    if _frontend_urls
    else ["*"]
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AppSettings(BaseModel):
    knowledge_base_enabled: bool = True
    llm_suggestions_enabled: bool = True
    image_enhancement_enabled: bool = True


app_settings = AppSettings()


def image_to_base64(image_bgr) -> str:
    ok, buffer = cv2.imencode(".jpg", image_bgr)
    if not ok:
        raise ValueError("Could not encode image")
    encoded = base64.b64encode(buffer).decode("utf-8")
    return f"data:image/jpeg;base64,{encoded}"


def top_predictions(result: dict, limit: int = 5) -> list[dict]:
    return [
        {"label": label, "confidence": probability}
        for label, probability in list(result["all_probs"].items())[:limit]
    ]


def model_quality(result: dict) -> dict:
    return result.get("quality", {})


# The skin model's "healthy / clear skin" class is literally named this.
SKIN_NORMAL_CLASS = "unknown_normal"
HEALTHY_SKIN_LABEL = "Healthy Skin"


def _prettify_label(raw: str) -> str:
    """Convert a raw model class name into a human-readable label.

    e.g. 'seborrh_keratoses' -> 'Seborrh Keratoses'.
    """
    return raw.replace("_", " ").strip().title()


def _resolve_skin_disease(result: dict) -> tuple[str, bool]:
    """Map a skin_disease model result to a display disease and a healthy flag.

    The model's ``unknown_normal`` class (clear / healthy skin) becomes
    "Healthy Skin". A low-confidence / uncertain prediction is also treated as
    healthy skin, because the classifier cannot confidently name any condition —
    which is what a clear-skin photo typically produces. This prevents random
    low-confidence disease names from being shown for clear skin. All other
    disease names are prettified for display.
    """
    raw = result["predicted_class"]
    is_uncertain = result.get("quality", {}).get("is_uncertain", False)
    if raw == SKIN_NORMAL_CLASS or is_uncertain:
        return HEALTHY_SKIN_LABEL, True
    return _prettify_label(raw), False


def dataset_explanation(recommendation: dict, herb: Optional[dict]) -> dict:
    return {
        "reasoning": "; ".join(recommendation.get("benefits", [])),
        "preparation_method": herb.get("preparation_method") if herb else None,
        "contraindications": herb.get("contraindications", []) if herb else [],
        "evidence_level": recommendation.get("evidence_level"),
    }


def process_image(contents: bytes):
    arr = np.frombuffer(contents, np.uint8)
    original = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if original is None:
        raise ValueError("Could not decode image")
    return original, original


@app.get("/")
def read_root():
    return {
        "status": "online",
        "message": "HerbalAI dataset inference API is active",
        "available_datasets": tf_available(),
    }


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.get("/api/settings", response_model=AppSettings)
def get_settings():
    return app_settings


@app.put("/api/settings", response_model=AppSettings)
def update_settings(settings: AppSettings):
    global app_settings
    app_settings = settings
    return app_settings


@app.get("/api/herbs")
def get_herbs():
    if not app_settings.knowledge_base_enabled:
        raise HTTPException(
            status_code=503, detail="Knowledge base is disabled in settings"
        )
    return get_all_herbs()


@app.get("/api/herbs/{name}")
def get_herb(name: str):
    if not app_settings.knowledge_base_enabled:
        raise HTTPException(
            status_code=503, detail="Knowledge base is disabled in settings"
        )
    herb = get_herb_by_name(name)
    if not herb:
        raise HTTPException(
            status_code=404, detail=f"No knowledge-base record for '{name}'"
        )
    return herb


@app.post("/api/predict/skin")
async def predict_skin(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        if not is_valid_domain("skin", contents):
            raise HTTPException(
                status_code=422,
                detail="This doesn't look like a skin photo. "
                "Please upload an image of the affected skin area only.",
            )
        result = tf_predict("skin_disease", contents)
        disease, is_healthy = _resolve_skin_disease(result)
        confidence = result["confidence"]
        original, enhanced = process_image(contents)

        recommendations = []
        herb_names = []
        if app_settings.knowledge_base_enabled:
            recommendation_result = RecommenderService.recommend(disease, confidence)
            for recommendation in recommendation_result["top_recommendations"]:
                herb = get_herb_by_name(recommendation["name"])
                herb_names.append(recommendation["name"])
                recommendations.append(
                    {
                        **recommendation,
                        "explanation": dataset_explanation(recommendation, herb),
                    }
                )

        llm_summary = None
        llm_error = None
        if app_settings.llm_suggestions_enabled:
            llm_summary = await run_in_threadpool(
                llm_service.generate_diagnosis_summary, disease, herb_names
            )
            llm_error = None if llm_summary else llm_service.get_last_error()

        response_payload = {
            "disease": disease,
            "confidence_score": confidence,
            "top_predictions": top_predictions(result),
            "model_quality": model_quality(result),
            "classification_status": (
                "healthy"
                if is_healthy
                else "uncertain"
                if model_quality(result).get("is_uncertain")
                else "classified"
            ),
            "is_healthy": is_healthy,
            "prediction_source": "skin_disease_dataset",
            "original_image": image_to_base64(original),
            "enhanced_image": (
                image_to_base64(enhanced)
                if app_settings.image_enhancement_enabled
                else None
            ),
            "recommendations": recommendations,
            "llm_summary": llm_summary,
            "llm_error": llm_error,
            "llm_disclaimer": llm_service.LLM_DISCLAIMER if llm_summary else None,
        }
        await _persist_session(
            "skin", response_payload, image=response_payload.get("original_image")
        )
        return response_payload
    except HTTPException:
        raise
    except FileNotFoundError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except Exception as error:
        logger.exception("Skin prediction failed")
        raise HTTPException(status_code=500, detail=str(error)) from error


@app.post("/api/predict/leaf")
async def predict_leaf(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        if not is_valid_domain("leaf", contents):
            raise HTTPException(
                status_code=422,
                detail="This doesn't look like a leaf photo. "
                "Please upload an image of a leaf only.",
            )
        result = tf_predict("medicinal_leaves", contents)
        quality = model_quality(result)
        is_uncertain = quality.get("is_uncertain", False)
        herb_name = None if is_uncertain else result["predicted_class"]
        original, enhanced = process_image(contents)
        herb_details = (
            get_herb_by_name(herb_name)
            if app_settings.knowledge_base_enabled and herb_name
            else None
        )

        llm_summary = None
        llm_error = None
        if app_settings.llm_suggestions_enabled:
            llm_summary = await run_in_threadpool(
                llm_service.generate_leaf_summary,
                herb_name or result["predicted_class"],
            )
            llm_error = None if llm_summary else llm_service.get_last_error()

        response_payload = {
            "herb": herb_name or "Uncertain leaf",
            "confidence_score": result["confidence"],
            "top_predictions": top_predictions(result),
            "model_quality": quality,
            "classification_status": "uncertain" if is_uncertain else "classified",
            "raw_model_prediction": result["predicted_class"],
            "prediction_source": "medicinal_leaves_dataset",
            "original_image": image_to_base64(original),
            "enhanced_image": (
                image_to_base64(enhanced)
                if app_settings.image_enhancement_enabled
                else None
            ),
            "details": herb_details,
            "llm_summary": llm_summary,
            "llm_error": llm_error,
            "llm_disclaimer": llm_service.LLM_DISCLAIMER if llm_summary else None,
        }
        await _persist_session(
            "leaf", response_payload, image=response_payload.get("original_image")
        )
        return response_payload
    except HTTPException:
        raise
    except FileNotFoundError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except Exception as error:
        logger.exception("Leaf prediction failed")
        raise HTTPException(status_code=500, detail=str(error)) from error


@app.post("/api/predict/joint")
async def predict_joint(
    skin_file: UploadFile = File(...),
    leaf_file: UploadFile = File(...),
):
    try:
        skin_contents = await skin_file.read()
        leaf_contents = await leaf_file.read()
        if not is_valid_domain("skin", skin_contents):
            raise HTTPException(
                status_code=422,
                detail="This doesn't look like a skin photo. "
                "Please upload an image of the affected skin area only.",
            )
        if not is_valid_domain("leaf", leaf_contents):
            raise HTTPException(
                status_code=422,
                detail="This doesn't look like a leaf photo. "
                "Please upload an image of a leaf only.",
            )
        skin_result = tf_predict("skin_disease", skin_contents)
        leaf_result = tf_predict("medicinal_leaves", leaf_contents)
        disease, _skin_is_healthy = _resolve_skin_disease(skin_result)
        leaf_quality = model_quality(leaf_result)
        leaf_uncertain = leaf_quality.get("is_uncertain", False)
        herb_name = None if leaf_uncertain else leaf_result["predicted_class"]
        skin_original, _ = process_image(skin_contents)
        leaf_original, _ = process_image(leaf_contents)

        evaluation = None
        explanation = None
        if app_settings.knowledge_base_enabled and herb_name:
            result = RecommenderService.recommend(
                disease,
                skin_result["confidence"],
                classified_herb=herb_name,
                herb_confidence=leaf_result["confidence"],
            )
            evaluation = result["leaf_evaluation"]
            herb = get_herb_by_name(herb_name)
            if evaluation and herb:
                explanation = dataset_explanation(evaluation, herb)

        response_payload = {
            "disease": disease,
            "disease_confidence": skin_result["confidence"],
            "disease_top_predictions": top_predictions(skin_result),
            "herb": herb_name,
            "herb_display": herb_name or "Uncertain leaf",
            "herb_confidence": leaf_result["confidence"],
            "leaf_top_predictions": top_predictions(leaf_result),
            "leaf_model_quality": leaf_quality,
            "leaf_classification_status": (
                "uncertain" if leaf_uncertain else "classified"
            ),
            "leaf_raw_model_prediction": leaf_result["predicted_class"],
            "prediction_source": "trained_datasets",
            "skin_original": image_to_base64(skin_original),
            "leaf_original": image_to_base64(leaf_original),
            "evaluation": evaluation,
            "explanation": explanation,
        }
        await _persist_session(
            "joint",
            response_payload,
            image=response_payload.get("skin_original"),
        )
        return response_payload
    except HTTPException:
        raise
    except FileNotFoundError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except Exception as error:
        logger.exception("Joint prediction failed")
        raise HTTPException(status_code=500, detail=str(error)) from error


@app.get("/api/tf/datasets")
def tf_datasets():
    return {"available_datasets": tf_available()}


@app.post("/api/tf/predict/{dataset_name}")
async def tf_predict_endpoint(dataset_name: str, file: UploadFile = File(...)):
    try:
        image_bytes = await file.read()
        result = tf_predict(dataset_name, image_bytes)
        response_payload = {
            "dataset": dataset_name,
            "predicted_class": result["predicted_class"],
            "confidence": result["confidence"],
            "all_probabilities": result["all_probs"],
        }
        await _persist_session("tf", response_payload, dataset=dataset_name)
        return response_payload
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except Exception as error:
        logger.exception("Dataset prediction failed for %s", dataset_name)
        raise HTTPException(status_code=500, detail=str(error)) from error


@app.get("/api/sessions")
async def get_sessions(limit: int = 50, offset: int = 0, db=Depends(get_db)):
    """Return persisted diagnosis sessions, newest first."""
    if not DB_ENABLED:
        return {"sessions": [], "db_enabled": False}
    rows = (
        (
            await db.execute(
                select(SessionRecord)
                .order_by(desc(SessionRecord.created_at))
                .limit(limit)
                .offset(offset)
            )
        )
        .scalars()
        .all()
    )
    sessions = [
        {
            "id": r.id,
            "created_at": r.created_at.isoformat() if r.created_at else None,
            "session_type": r.session_type,
            "dataset": r.dataset,
            "predicted_class": r.predicted_class,
            "confidence": r.confidence,
            "status": r.status,
            "top_predictions": r.top_predictions,
            "recommendations": r.recommendations,
            "llm_summary": r.llm_summary,
            "image": r.image,
            "meta": r.meta,
        }
        for r in rows
    ]
    return {"sessions": sessions, "db_enabled": True}
