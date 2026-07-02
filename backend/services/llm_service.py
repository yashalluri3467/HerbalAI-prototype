import os
import requests
import json
import logging
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

logger = logging.getLogger("HerbalAI.LLMService")

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
if not OPENROUTER_API_KEY:
    logger.warning("OPENROUTER_API_KEY environment variable is not set. LLM features may fail.")

PRIMARY_MODEL = "nvidia/nemotron-3-super-120b-a12b:free"
# Free vision models (tested and working)
VISION_PRIMARY_MODEL = "google/gemma-4-26b-a4b-it:free"
VISION_FALLBACK_MODEL = "nvidia/nemotron-nano-12b-v2-vl:free"

HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "http://localhost:5173",
    "X-Title": "Ayurvedic AI"
}

def _safe_extract_content(data: dict) -> str:
    """Safely extract content from OpenRouter response, handling missing 'choices' key."""
    try:
        return data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, TypeError) as e:
        # Log the actual response for debugging
        logger.warning(f"Unexpected API response structure: {str(data)[:200]}")
        return ""


def generate_diagnosis_summary(disease: str, herbs: list) -> str:
    """
    Generates a single LLM summary for the entire skin diagnosis result.
    Covers: what the disease is, why the recommended herbs help, and general advice.
    """
    herbs_str = ", ".join(herbs[:3]) if herbs else "various Ayurvedic herbs"
    
    prompt = (
        f"The patient has been diagnosed with '{disease}' by our AI skin analysis model. "
        f"The top recommended Ayurvedic herbs are: {herbs_str}. "
        f"Provide a concise summary (4-5 sentences) that: "
        f"1) Briefly explains what {disease} is, "
        f"2) Why these specific herbs are beneficial for it, "
        f"3) Any general Ayurvedic lifestyle advice for this condition."
    )
    
    payload = {
        "model": PRIMARY_MODEL,
        "messages": [
            {"role": "system", "content": "You are an expert Ayurvedic dermatologist. Provide concise, clinical, and accurate explanations. Do not use markdown formatting."},
            {"role": "user", "content": prompt}
        ]
    }
    
    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=HEADERS, json=payload, timeout=20)
        response.raise_for_status()
        data = response.json()
        content = _safe_extract_content(data)
        return content if content else ""
    except Exception as e:
        logger.error(f"LLM diagnosis summary error: {e}")
        return ""


def generate_leaf_summary(herb: str) -> str:
    """
    Generates a single LLM summary for an identified herb leaf.
    """
    prompt = (
        f"The AI has identified the plant leaf as '{herb}'. "
        f"Provide a concise summary (3-4 sentences) covering: "
        f"1) What this herb is and its botanical significance, "
        f"2) Its primary medicinal uses in Ayurveda (especially for skin), "
        f"3) How it is typically prepared or applied."
    )
    
    payload = {
        "model": PRIMARY_MODEL,
        "messages": [
            {"role": "system", "content": "You are an expert Ayurvedic botanist. Provide concise, clinical, and accurate explanations. Do not use markdown formatting."},
            {"role": "user", "content": prompt}
        ]
    }
    
    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=HEADERS, json=payload, timeout=20)
        response.raise_for_status()
        data = response.json()
        content = _safe_extract_content(data)
        return content if content else ""
    except Exception as e:
        logger.error(f"LLM leaf summary error: {e}")
        return ""


def fallback_image_classification(base64_image: str, mode: str) -> str:
    """
    Uses a free vision model to classify an image when the local CNN has low confidence.
    Mode should be 'skin' or 'leaf'.
    """
    if mode == 'skin':
        prompt = (
            "Analyze this skin image carefully. Identify the skin disease or condition shown. "
            "Reply ONLY with the disease name (e.g., 'Acne', 'Eczema', 'Psoriasis', 'Pigmentation', "
            "'Dry Skin', 'Wrinkles', 'Rosacea', or 'Healthy Skin'). Nothing else."
        )
    else:
        prompt = (
            "Analyze this plant leaf image carefully. Identify the medicinal herb. "
            "Reply ONLY with the common name of the herb (e.g., 'Neem', 'Aloe Vera', 'Turmeric', "
            "'Tulsi', 'Amla', 'Moringa', 'Hibiscus', 'Ashwagandha', 'Bhringraj'). Nothing else."
        )
    
    # Strip data URI prefix if present (image_to_base64 adds it)
    clean_b64 = base64_image
    if clean_b64.startswith("data:"):
        clean_b64 = clean_b64.split(",", 1)[1]
    
    payload = {
        "model": VISION_PRIMARY_MODEL,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{clean_b64}"
                        }
                    }
                ]
            }
        ]
    }
    
    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=HEADERS, json=payload, timeout=25)
        data = response.json()
        content = _safe_extract_content(data)
        
        if content:
            return content
        
        # If primary vision model fails, try fallback
        logger.warning(f"Primary vision model returned empty, falling back to {VISION_FALLBACK_MODEL}")
        payload["model"] = VISION_FALLBACK_MODEL
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=HEADERS, json=payload, timeout=25)
        data = response.json()
        content = _safe_extract_content(data)
        return content if content else "Unknown"
        
    except Exception as e:
        logger.error(f"LLM image classification error: {e}")
        return "Unknown"
