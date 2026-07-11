# backend/utils/merge_skin_datasets.py
"""Merge the skin datasets under D:\\skin datasets into backend/data/skin_disease/prepared.

The live trainer (utils/train_tf_models.py) consumes a class-per-folder layout directly
from ``data/<name>/prepared``. This script gathers the relevant skin-condition datasets into
that layout while:

* keeping the canonical 22-class taxonomy defined by dataset 6 (the Kaggle
  ``pacificrm/skindiseasedataset`` set that already powers the deployed ``skin_disease`` model),
* augmenting only *clearly-matching* classes from the other five sources via a synonym map
  (acne / eczema / rosacea / tinea / skin-cancer / benign-tumour / seborrhoeic-keratosis /
  vascular-tumour / sun-damage), skipping classes with no clean canonical fit,
* normalising labels (lowercased, spaces/dots/hyphens -> '_', leading numeric prefixes
  stripped e.g. ``"3. Akne"`` -> ``akne``),
* capping each canonical class at ``MAX_PER_CLASS`` images (deterministic seeded sample) so
  one huge source (e.g. dataset 4) cannot drown the others and CPU training stays bounded,
* writing ``merge_manifest.json`` describing the resulting mapping.

Run:
    python -m utils.merge_skin_datasets
    python -m utils.merge_skin_datasets --source "D:/skin datasets" --max-per-class 700
    python -m utils.merge_skin_datasets --force      # rebuild even if prepared/ exists
"""

import argparse
import json
import logging
import random
import re
import shutil
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("HerbalAI.MergeSkin")

# Ensure the backend package root is importable when run as a script.
_BACKEND = Path(__file__).resolve().parent.parent
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

DEST = _BACKEND / "data" / "skin_disease" / "prepared"
MAX_PER_CLASS = 700
IMG_EXTS = {".jpg", ".jpeg", ".png", ".bmp"}  # webp excluded (unreliable in TF decode)

# Canonical taxonomy = dataset 6's 22 classes (normalised). This is the label set the deployed
# skin_disease model predicts, and it aligns with the knowledge-base disease_mapping keys
# (acne / eczema / psoriasis / rosacea / vitiligo) that the recommender resolves.
CANONICAL = [
    "acne", "actinic_keratosis", "benign_tumors", "bullous", "candidiasis", "drugeruption",
    "eczema", "infestations_bites", "lichen", "lupus", "moles", "psoriasis", "rosacea",
    "seborrh_keratoses", "skincancer", "sun_sunlight_damage", "tinea", "unknown_normal",
    "vascular_tumors", "vasculitis", "vitiligo", "warts",
]
CANONICAL_SET = set(CANONICAL)

# Raw (normalised) label -> canonical label. Only clear matches are mapped; anything not in
# CANONICAL_SET and not here is skipped + logged. "Enfeksiyonel" (heterogeneous infectious
# bucket), "herpes", "bags"/"redness" (cosmetic), and the bacterial/viral ds1 classes are
# intentionally left unmapped to avoid label noise.
SYNONYMS = {
    # dataset 1 (BA/FU/VI/PA coded) — only the fungal classes map cleanly to tinea
    "fu_athlete_foot": "tinea",
    "fu_nail_fungus": "tinea",
    "fu_ringworm": "tinea",
    # dataset 3 (ISIC lesions)
    "dermatofibroma": "benign_tumors",
    "melanoma": "skincancer",
    "pigmented_benign_keratosis": "seborrh_keratoses",
    "seborrheic_keratosis": "seborrh_keratoses",
    "squamous_cell_carcinoma": "skincancer",
    "vascular_lesion": "vascular_tumors",
    # dataset 4 (Turkish, "N. Name" folders)
    "ekzama": "eczema",
    "akne": "acne",
    "pigment": "sun_sunlight_damage",   # closest of the 22 canonical classes
    "benign": "benign_tumors",
    "malign": "skincancer",
    # dataset 5 (Roboflow)
    "eksim": "eczema",
    "panu": "tinea",                    # panu = tinea versicolor
    "rosacea": "rosacea",
    # dataset 2 (CSV-indexed cosmetic, only the acne type maps)
    "acne": "acne",
}


def normalize(name: str) -> str:
    """Turn a raw folder/class name into a normalised label."""
    label = (name or "").strip().lower()
    label = re.sub(r"[^a-z0-9]+", "_", label)   # spaces / dots / hyphens -> _
    label = re.sub(r"^_+|_+$", "", label)
    label = re.sub(r"^(\d+)_", "", label)        # strip leading "3_" etc.
    return label


def map_label(raw_name: str):
    """Return the canonical label for a raw class folder name, or None to skip."""
    n = normalize(raw_name)
    if n in CANONICAL_SET:
        return n
    return SYNONYMS.get(n)


def collect_images(folder: Path) -> list[Path]:
    return [p for p in folder.rglob("*") if p.suffix.lower() in IMG_EXTS and p.is_file()]


def main(source_root: Path, max_per_class: int, force: bool) -> int:
    if not source_root.is_dir():
        logger.error("Source root not found: %s", source_root)
        return 1

    # (tag, root containing class sub-folders, ...)
    sources = [
        ("ds6_train", source_root / "skin disease 6" / "train"),
        ("ds6_test", source_root / "skin disease 6" / "test"),
        ("ds3", source_root / "skin disease 3" / "skin_disease"),
        ("ds4_train", source_root / "skin disease 4" / "kaggle" / "train"),
        ("ds5_train", source_root / "skin disease 5" / "train"),
        ("ds1_train", source_root / "skin disease 1" / "skin-disease-datasaet" / "train_set"),
        ("ds1_test", source_root / "skin disease 1" / "skin-disease-datasaet" / "test_set"),
        ("ds2", source_root / "skin disease 2" / "files"),
    ]

    missing = [str(root) for _, root in sources if not root.is_dir()]
    if missing:
        logger.error("Missing source dataset folder(s):\n  %s", "\n  ".join(missing))
        return 1

    if DEST.exists():
        if force:
            logger.warning("Removing existing %s for a clean merge.", DEST)
            shutil.rmtree(DEST)
        else:
            logger.warning(
                "%s already exists. Use --force to rebuild. Aborting.", DEST
            )
            return 0

    # canonical -> {"sources": {tag: orig_folder}, "images": [Path,...]}
    classes: dict[str, dict] = {c: {"sources": {}, "images": []} for c in CANONICAL}
    skipped: dict[str, int] = {}

    for tag, root in sources:
        logger.info("Scanning %s (%s) ...", tag, root)
        for class_folder in sorted(p for p in root.iterdir() if p.is_dir()):
            canonical = map_label(class_folder.name)
            if canonical is None:
                skipped[class_folder.name] = skipped.get(class_folder.name, 0) + 1
                logger.info("  skip (no canonical match): %s", class_folder.name)
                continue
            entry = classes[canonical]
            entry["sources"][tag] = class_folder.name
            entry["images"].extend(collect_images(class_folder))

    DEST.mkdir(parents=True, exist_ok=True)
    rng = random.Random(42)

    manifest = {
        "classes": {},
        "skipped_classes": skipped,
        "max_per_class": max_per_class,
        "total_images": 0,
    }
    final_count = 0
    total_images = 0

    for label in CANONICAL:
        entry = classes[label]
        images = entry["images"]
        if not images:
            manifest["classes"][label] = {"sources": entry["sources"], "image_count": 0}
            continue
        if len(images) > max_per_class:
            # Deterministic sample so no single source dominates the canonical class.
            rng.shuffle(images)
            images = images[:max_per_class]
        dest_dir = DEST / label
        dest_dir.mkdir(parents=True, exist_ok=True)
        for img in images:
            dest_name = f"{img.parent.name}__{img.name}"
            shutil.copy2(img, dest_dir / dest_name)
        final_count += 1
        total_images += len(images)
        manifest["classes"][label] = {
            "sources": entry["sources"],
            "image_count": len(images),
        }

    manifest["final_class_count"] = final_count
    manifest["total_images"] = total_images
    (DEST.parent / "merge_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    logger.info(
        "Merge complete: %d/%d canonical classes, %d images -> %s",
        final_count, len(CANONICAL), total_images, DEST,
    )
    logger.info("Manifest written to %s", DEST.parent / "merge_manifest.json")
    if skipped:
        logger.info("Skipped classes (no canonical match): %s", sorted(skipped))
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge skin datasets into prepared layout")
    parser.add_argument(
        "--source", default=r"D:/skin datasets",
        help="Root directory containing the 'skin disease N' folders",
    )
    parser.add_argument(
        "--max-per-class", type=int, default=MAX_PER_CLASS,
        help="Maximum images kept per canonical class (default 700)",
    )
    parser.add_argument(
        "--force", action="store_true",
        help="Rebuild even if prepared/ already exists",
    )
    args = parser.parse_args()
    sys.exit(main(Path(args.source), args.max_per_class, args.force))
