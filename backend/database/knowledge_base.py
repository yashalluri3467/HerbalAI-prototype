import json
import re
from pathlib import Path

DATASET_PATH = (
    Path(__file__).resolve().parent.parent / "datasets" / "herbal_knowledge_base.json"
)


def _load_database() -> dict:
    if not DATASET_PATH.is_file():
        return {}
    with DATASET_PATH.open("r", encoding="utf-8") as dataset_file:
        data = json.load(dataset_file)
    if not isinstance(data, dict):
        raise ValueError("Herbal knowledge-base dataset must contain a JSON object")
    return data


HERB_DATABASE = _load_database()


def _normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", (value or "").casefold())


def get_herb_by_name(name):
    normalized_name = _normalize(name)
    if not normalized_name:
        return None

    for herb_name, herb in HERB_DATABASE.items():
        candidates = (
            herb_name,
            herb.get("name", ""),
            herb.get("botanical_name", ""),
        )
        if normalized_name in {_normalize(candidate) for candidate in candidates}:
            return herb
    return None


def get_recommendations_for_disease(disease, min_efficacy=0):
    normalized_disease = (disease or "").replace("_", " ").strip().casefold()
    recommendations = []

    for name, data in HERB_DATABASE.items():
        matched_disease = next(
            (
                label
                for label in data.get("disease_mapping", {})
                if label.casefold() == normalized_disease
            ),
            None,
        )
        if not matched_disease:
            continue

        mapping = data["disease_mapping"][matched_disease]
        if mapping["efficacy"] < min_efficacy:
            continue

        recommendations.append(
            {
                "name": name,
                "botanical_name": data["botanical_name"],
                "efficacy": mapping["efficacy"],
                "weight": mapping["weight"],
                "benefits": data["benefits"],
                "evidence_level": data["evidence_level"],
            }
        )

    return sorted(
        recommendations,
        key=lambda recommendation: recommendation["efficacy"],
        reverse=True,
    )


def get_all_herbs():
    return list(HERB_DATABASE.values())
