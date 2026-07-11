# backend/utils/merge_leaf_datasets.py
"""Merge all D:\\Herbal project leaf datasets into backend/data/medicinal_leaves/prepared.

The live trainer (utils/train_tf_models.py) consumes a class-per-folder layout directly
from ``data/<name>/prepared``. This script gathers the four leaf datasets shipped in
``D:\\Herbal project`` into that layout with:

* label normalization (lowercased, spaces/hyphens -> '_', trailing '(Common Name)' used
  for MED117 botanical folders),
* same-label merging across sources (so Aloevera from two sets becomes one class),
* a per-class image cap to keep CPU training time bounded,
* a ``merge_manifest.json`` describing the resulting mapping.

Run:
    python -m utils.merge_leaf_datasets
"""

import json
import random
import re
import shutil
import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("HerbalAI.Merge")

# Ensure the backend package root is importable when run as a script.
_BACKEND = Path(__file__).resolve().parent.parent
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

DEST = _BACKEND / "data" / "medicinal_leaves" / "prepared"
MAX_PER_CLASS = 150
IMG_EXTS = {".jpg", ".jpeg", ".png", ".bmp"}

# Source roots (order defines merge priority: earlier sources win the label name).
SOURCES = [
    ("s1", Path(r"D:/Herbal project/leaf dataset/Indian Medicinal Leaves Image Datasets/Medicinal Leaf dataset")),
    ("s2", Path(r"D:/Herbal project/leaf dataset/Indian Medicinal Leaves Image Datasets/Medicinal plant dataset")),
    ("s3", Path(r"D:/Herbal project/MED117_Medicinal Plant Leaf Dataset & Name Table/MED117_Medicinal Plant Leaf Dataset & Name Table/MED 117 Leaf Species/Raw leaf image set of Medicinal plants_v2")),
    ("s4", Path(r"D:/Herbal project/archive/Medicinal Plant Identification Dataset/Original-Images-Version-02")),
]

# Catch the obvious name variants so clean-set dupes collapse to one class.
SYNONYMS = {
    "aloevera": "aloe_vera",
    "amruthaballi": "amruta_balli",
    "ashoka": "ashoka",
    "arali": "arali",
}


def normalize(name: str) -> str:
    """Turn a raw folder name into a usable class label."""
    # Prefer a trailing "(Common Name)" parenthetical (MED117 uses these).
    m = re.search(r"\(([^()]+)\)\s*$", name)
    if m:
        candidate = m.group(1).strip()
        if candidate:
            name = candidate
    label = name.strip().lower()
    # Drop any remaining parentheses (e.g. "(L.) Correa").
    label = re.sub(r"\([^()]*\)", "", label)
    label = label.replace("-", "_").replace(" ", "_")
    label = re.sub(r"[^a-z0-9_]", "", label)
    label = label.strip("_")
    return SYNONYMS.get(label, label) or label


def collect_images(folder: Path) -> list[Path]:
    return [p for p in folder.rglob("*") if p.suffix.lower() in IMG_EXTS and p.is_file()]


def main() -> int:
    missing = [str(src) for _, src in SOURCES if not src.is_dir()]
    if missing:
        logger.error("Missing source dataset(s):\n  %s", "\n  ".join(missing))
        return 1

    # label -> { "sources": {source_tag: orig_folder_name}, "images": [Path,...] }
    classes: dict[str, dict] = {}

    for tag, root in SOURCES:
        logger.info("Scanning %s (%s) ...", tag, root)
        for class_folder in sorted(p for p in root.iterdir() if p.is_dir()):
            label = normalize(class_folder.name)
            if not label:
                logger.warning("Skipping un-nameable folder: %s", class_folder)
                continue
            entry = classes.setdefault(
                label, {"sources": {}, "images": []}
            )
            entry["sources"][tag] = class_folder.name
            entry["images"].extend(collect_images(class_folder))

    # Write merged, capped layout.
    if DEST.exists():
        logger.warning("Removing existing %s for a clean merge.", DEST)
        shutil.rmtree(DEST)
    DEST.mkdir(parents=True, exist_ok=True)

    manifest = {"classes": {}, "total_images": 0, "max_per_class": MAX_PER_CLASS}
    final_count = 0
    total_images = 0

    for label, entry in sorted(classes.items()):
        images = entry["images"]
        if len(images) > MAX_PER_CLASS:
            # Keep a deterministic-ish sample (sorted for stability across runs).
            images = sorted(images, key=lambda p: p.name)[:MAX_PER_CLASS]
        if not images:
            continue
        dest_dir = DEST / label
        dest_dir.mkdir(parents=True, exist_ok=True)
        for img in images:
            # Avoid name clashes across sources by prefixing the source tag.
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
        "Merge complete: %d classes, %d images -> %s",
        final_count, total_images, DEST,
    )
    logger.info("Manifest written to %s", DEST.parent / "merge_manifest.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
