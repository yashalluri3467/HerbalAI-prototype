import os
import requests
import json
import logging
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

logger = logging.getLogger("HerbalAI.LLMService")

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
if not OPENROUTER_API_KEY:
    logger.warning("OPENROUTER_API_KEY environment variable is not set. LLM features may fail.")

PRIMARY_MODEL = os.environ.get("OPENROUTER_MODEL", "openrouter/auto")
LAST_ERROR = None

LLM_DISCLAIMER = (
    "AI-generated summary for informational use only — not medical advice. "
    "Consult a qualified practitioner."
)

HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "http://localhost:5173",
    "X-Title": "Ayurvedic AI"
}


def _set_last_error(message: str):
    global LAST_ERROR
    LAST_ERROR = message
    logger.error(message)


def get_last_error():
    return LAST_ERROR

def _safe_extract_content(data: dict) -> str:
    """Safely extract content from OpenRouter response, handling missing 'choices' key."""
    try:
        return data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, TypeError) as e:
        logger.warning(f"Unexpected API response structure: {str(data)[:200]}")
        return ""

def generate_diagnosis_summary(disease: str, herbs: list) -> str:
    """
    Generates a single LLM summary for the entire skin diagnosis result, GROUNDED in the
    knowledge base. Returns None (no fabrication) when no recommended herb resolves in the KB.
    """
    if not OPENROUTER_API_KEY:
        _set_last_error("OPENROUTER_API_KEY is missing. Add it to backend/.env and restart the API.")
        return None

    from database.knowledge_base import get_herb_by_name

    resolved = []
    for herb in (herbs or [])[:3]:
        data = get_herb_by_name(herb)
        if not data:
            continue
        compounds = ", ".join(data.get("active_compounds", [])[:3])
        benefits = "; ".join(data.get("benefits", [])[:2])
        resolved.append(f"{herb}: known compounds [{compounds}]; documented benefits [{benefits}]")

    if not resolved:
        _set_last_error(
            f"No knowledge-base entries for the recommended herbs {herbs}; "
            "summary omitted to avoid fabrication."
        )
        return None

    herbs_block = " | ".join(resolved)
    prompt = (
        f"The patient has been diagnosed with '{disease}' by our AI skin analysis model. "
        f"Knowledge-base-backed information about the recommended herbs: {herbs_block}. "
        f"Provide a short, reasonable summary in 1-2 sentences that: "
        f"1) briefly explains what {disease} is, "
        f"2) says why these herbs are helpful for it based only on the provided facts, "
        f"3) avoids inventing any properties not listed above. "
        f"Do not use markdown formatting."
    )

    payload = {
        "model": PRIMARY_MODEL,
        "messages": [
            {"role": "system", "content": "You are an expert Ayurvedic dermatologist. Provide concise, clinical, and accurate explanations based only on the provided facts. Do not use markdown formatting."},
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=HEADERS, json=payload, timeout=20)
        response.raise_for_status()
        data = response.json()
        content = _safe_extract_content(data)
        if content:
            return content
    except Exception as e:
        detail = getattr(getattr(e, "response", None), "text", "")
        _set_last_error(f"LLM diagnosis summary error: {e}. {detail[:300]}")
    return None


def generate_leaf_summary(herb: str) -> str:
    """
    Generates a single LLM summary for an identified herb leaf, GROUNDED in the knowledge base.
    Returns None (no fabrication) when the herb has no knowledge-base entry.
    """
    if not OPENROUTER_API_KEY:
        _set_last_error("OPENROUTER_API_KEY is missing. Add it to backend/.env and restart the API.")
        return None

    from database.knowledge_base import get_herb_by_name

    herb_data = get_herb_by_name(herb)
    if not herb_data:
        _set_last_error(
            f"No knowledge-base entry for '{herb}'; summary omitted to avoid fabrication."
        )
        return None

    compounds = ", ".join(herb_data.get("active_compounds", [])[:3])
    phyto = ", ".join(herb_data.get("phytochemicals", [])[:3])
    benefits = "; ".join(herb_data.get("benefits", [])[:3])
    prompt = (
        f"The identified herb is '{herb}' (botanical name: {herb_data.get('botanical_name', '')}). "
        f"Known active compounds: {compounds}. Phytochemicals: {phyto}. "
        f"Documented benefits: {benefits}. Evidence level: {herb_data.get('evidence_level', '')}. "
        f"Write a short, reasonable summary in 1-2 sentences using ONLY the information above. "
        f"Do not invent properties. Mention typical preparation: {herb_data.get('preparation_method', '')}."
    )

    payload = {
        "model": PRIMARY_MODEL,
        "messages": [
            {"role": "system", "content": "You are an expert Ayurvedic botanist. Provide concise, clinical, and accurate explanations based only on the provided facts. Do not use markdown formatting."},
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=HEADERS, json=payload, timeout=20)
        response.raise_for_status()
        data = response.json()
        content = _safe_extract_content(data)
        if content:
            return content
    except Exception as e:
        detail = getattr(getattr(e, "response", None), "text", "")
        _set_last_error(f"LLM leaf summary error: {e}. {detail[:300]}")
    return None
