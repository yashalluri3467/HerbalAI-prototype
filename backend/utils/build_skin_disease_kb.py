#!/usr/bin/env python3
"""Build a skin-disease knowledge base JSON from the repo's authoritative sources.

Sources (all read-only):
  - backend/models/skin_disease/class_names.txt   -> 22 model classes (source of truth, order preserved)
  - backend/data/skin_disease/prepared/<class>/    -> training-image counts
  - backend/datasets/herbal_knowledge_base.json    -> herbal remedy cross-reference (disease_mapping)

Output:
  - backend/datasets/skin_disease_knowledge_base.json

No medical text is authored here: every field comes from an existing repo file. Herbal links are
resolved through the explicit CLASS_TO_HERBAL_KEY alias map so only connections present in the source
are included.
"""
from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]  # backend/
MODELS_DIR = REPO_ROOT / "models" / "skin_disease"
PREPARED_DIR = REPO_ROOT / "data" / "skin_disease" / "prepared"
HERBAL_KB = REPO_ROOT / "datasets" / "herbal_knowledge_base.json"
OUT_PATH = REPO_ROOT / "datasets" / "skin_disease_knowledge_base.json"

# Curated human-readable labels for the raw class keys (pure name formatting, no medical authoring).
LABELS = {
    "acne": "Acne",
    "actinic_keratosis": "Actinic Keratosis",
    "benign_tumors": "Benign Tumors",
    "bullous": "Bullous Disease",
    "candidiasis": "Candidiasis",
    "drugeruption": "Drug Eruption",
    "eczema": "Eczema",
    "infestations_bites": "Infestations & Bites",
    "lichen": "Lichenoid Disorders",
    "lupus": "Lupus (Cutaneous)",
    "moles": "Moles / Nevi",
    "psoriasis": "Psoriasis",
    "rosacea": "Rosacea",
    "seborrh_keratoses": "Seborrheic Keratoses",
    "skincancer": "Skin Cancer",
    "sun_sunlight_damage": "Sun / Sunlight Damage",
    "tinea": "Tinea (Fungal)",
    "unknown_normal": "Unknown / Normal",
    "vascular_tumors": "Vascular Tumors",
    "vasculitis": "Vasculitis",
    "vitiligo": "Vitiligo",
    "warts": "Warts",
}

# Maps a model class to the disease key(s) used in the herbal KB's disease_mapping.
# Only links that actually exist in the source are listed (no inferred/guessed links).
CLASS_TO_HERBAL_KEY = {
    "acne": ["Acne"],
    "eczema": ["Eczema"],
    "psoriasis": ["Psoriasis"],
    "rosacea": ["Rosacea"],
    "vitiligo": ["Vitiligo"],
    "candidiasis": ["Fungal Infection"],
    "tinea": ["Fungal Infection"],
    "unknown_normal": ["Healthy Skin"],
}


def load_class_names() -> list[str]:
    text = (MODELS_DIR / "class_names.txt").read_text(encoding="utf-8")
    return [line.strip() for line in text.splitlines() if line.strip()]


def count_images(class_name: str) -> int:
    folder = PREPARED_DIR / class_name
    if not folder.is_dir():
        return 0
    return sum(1 for p in folder.iterdir() if p.is_file())


def load_herbal_kb() -> dict:
    return json.loads(HERBAL_KB.read_text(encoding="utf-8"))


def build() -> dict:
    class_names = load_class_names()
    herbal = load_herbal_kb()

    diseases: list[dict] = []
    for cls in class_names:
        remedies: list[dict] = []
        for herb_name, herb in herbal.items():
            mapping = herb.get("disease_mapping", {})
            for key in CLASS_TO_HERBAL_KEY.get(cls, []):
                if key in mapping:
                    m = mapping[key]
                    remedies.append(
                        {
                            "herb": herb_name,
                            "efficacy": m.get("efficacy"),
                            "weight": m.get("weight"),
                            "evidence_level": herb.get("evidence_level"),
                            "preparation_method": herb.get("preparation_method"),
                        }
                    )
        remedies.sort(key=lambda r: r.get("efficacy") or 0, reverse=True)
        diseases.append(
            {
                "id": cls,
                "label": LABELS.get(cls, cls.replace("_", " ").title()),
                "training_images": count_images(cls),
                "remedies": remedies,
            }
        )

    return {
        "metadata": {
            "source": "class_names.txt + prepared training images + herbal_knowledge_base.json",
            "num_diseases": len(diseases),
            "herbal_link_note": (
                "remedies are cross-referenced from herbal_knowledge_base.json via an explicit "
                "alias map; classes with no mapped remedy have an empty remedies list."
            ),
        },
        "diseases": diseases,
    }


def main() -> None:
    kb = build()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(kb, indent=2, ensure_ascii=False), encoding="utf-8")
    linked = sum(1 for d in kb["diseases"] if d["remedies"])
    print(f"Wrote {OUT_PATH}")
    print(f"Diseases: {kb['metadata']['num_diseases']}")
    print(f"Diseases with >=1 herbal remedy: {linked}")


if __name__ == "__main__":
    main()
