# backend/utils/tf_preprocess.py
"""TensorFlow dataset preparation and preprocessing utilities.

These datasets require manual download (they use authentication / gated access).
Place the raw downloaded archives/folders in the paths shown in DATASET_SPECS
under the "local_path" key before running the training script.

Manual download steps
---------------------
1. mendeley        → https://data.mendeley.com/datasets/dtvbwrhznz/4
                     Download the ZIP, place it at:  data/mendeley/raw.zip
2. medicinal_leaves→ https://www.kaggle.com/datasets/aryashah2k/indian-medicinal-leaves-dataset
                     Download via Kaggle CLI or browser, place ZIP at:  data/medicinal_leaves/raw.zip
3. isic            → https://challenge.isic-archive.com/data/
                     Download images + ground truth CSV, place them in:  data/isic/raw/
4. skin_disease    → merged from the six sources under D:\\skin datasets
                     Run:  python -m utils.merge_skin_datasets
                     then: python -m utils.train_tf_models --dataset skin_disease --train-both

After preparing the data, run:
    python -m utils.train_tf_models --dataset <name> --epochs 15 --batch-size 32

The module provides:
1. ``prepare_dataset(name)`` – extracts/reorganises data into ``data/<name>/prepared``
   where each sub-folder is a class label (required by ``image_dataset_from_directory``).
2. ``load_tf_dataset(name, ...)`` – returns an augmented, normalised ``tf.data.Dataset``
   ready for model.fit().
"""

import os
import pathlib
import zipfile
import shutil
import csv
import tensorflow as tf

# ---------------------------------------------------------------------------
# BASE directory – always relative to the backend/ folder so the script works
# regardless of the CWD.
# ---------------------------------------------------------------------------
_BACKEND_DIR = pathlib.Path(__file__).resolve().parent.parent
BASE_DATA_DIR = _BACKEND_DIR / "data"
BASE_DATA_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# Dataset specs – update "local_zip" or "local_raw" if you stored files elsewhere.
# ---------------------------------------------------------------------------
DATASET_SPECS = {
    "mendeley": {
        # If you downloaded the zip manually place it at data/mendeley/raw.zip
        # OR place extracted images in data/mendeley/raw/<class_folders>/
        "local_zip": BASE_DATA_DIR / "mendeley" / "raw.zip",
        "local_raw": BASE_DATA_DIR / "mendeley" / "raw",
        "class_source": "folders",
        "description": "Mendeley skin-disease image dataset (dtvbwrhznz/4)",
    },
    "medicinal_leaves": {
        # Merged from all D:\\Herbal project leaf datasets via utils.merge_leaf_datasets.
        # The merge script writes the class-per-folder layout directly into this dir.
        "local_raw": BASE_DATA_DIR / "medicinal_leaves" / "prepared",
        "class_source": "folders",
        "description": "Merged medicinal-leaf datasets (D:\\Herbal project)",
    },
    "isic": {
        # ISIC usually comes as a folder of images + a CSV – no zip expected.
        "local_raw": BASE_DATA_DIR / "isic" / "raw",
        "class_source": "csv",
        "description": "ISIC skin-lesion challenge dataset",
    },
    "skin_disease": {
        # Built from the six sources under D:\\skin datasets by
        # utils.merge_skin_datasets (canonical 22-class taxonomy from dataset 6,
        # augmented with clearly-matching classes from the other sets).
        "local_raw": BASE_DATA_DIR / "skin_disease" / "prepared",
        "class_source": "folders",
        "description": "Merged skin-condition datasets (D:\\skin datasets)",
    },
}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _extract_zip(zip_path: pathlib.Path, extract_dir: pathlib.Path) -> pathlib.Path:
    """Extract a ZIP archive to *extract_dir* (skips if already extracted)."""
    if extract_dir.exists() and any(extract_dir.iterdir()):
        return extract_dir
    extract_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(extract_dir)
    return extract_dir


def _flatten_folder_structure(root: pathlib.Path, target: pathlib.Path, class_source: str):
    """Re-organise *root* into ``target/<class>/`` layout.

    * ``folders`` – each immediate sub-directory of *root* is a class label.
    * ``csv``     – a CSV with columns ``image_path`` (or ``image``) and
                    ``label`` (or ``dx``) maps images to classes.
    """
    if class_source == "folders":
        # Walk up to two levels deep to find class directories
        # (some ZIPs have an extra wrapper folder at the top)
        candidates = [d for d in root.iterdir() if d.is_dir()]
        if len(candidates) == 1 and not any(
            f.suffix.lower() in {".jpg", ".jpeg", ".png"}
            for f in candidates[0].iterdir()
            if f.is_file()
        ):
            # Unwrap one extra nesting level
            root = candidates[0]
            candidates = [d for d in root.iterdir() if d.is_dir()]

        if not candidates:
            raise FileNotFoundError(
                f"No class sub-directories found under {root}. "
                "Make sure the archive was extracted correctly."
            )

        for class_dir in candidates:
            label = class_dir.name.strip().replace(" ", "_").lower()
            dest = target / label
            dest.mkdir(parents=True, exist_ok=True)
            for img in class_dir.rglob("*"):
                if img.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp"}:
                    shutil.copy2(img, dest / img.name)

    elif class_source == "csv":
        csv_path = None
        for p in root.rglob("*.csv"):
            csv_path = p
            break
        if csv_path is None:
            raise FileNotFoundError(
                f"CSV label file not found under {root}. "
                "ISIC data should include a GroundTruth CSV."
            )
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                img_rel = row.get("image_path") or row.get("image") or row.get("isic_id")
                label = row.get("label") or row.get("dx") or row.get("diagnosis")
                if not img_rel or not label:
                    continue
                # Try to find the image file
                src = root / img_rel
                if not src.is_file():
                    # Try with common extensions
                    for ext in (".jpg", ".jpeg", ".png"):
                        candidate = root / (img_rel + ext)
                        if candidate.is_file():
                            src = candidate
                            break
                if not src.is_file():
                    continue
                lbl = label.strip().replace(" ", "_").lower()
                dest = target / lbl
                dest.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dest / src.name)
    else:
        raise ValueError(f"Unsupported class_source: {class_source!r}")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def prepare_dataset(name: str) -> pathlib.Path:
    """Prepare ``data/<name>/prepared`` for ``image_dataset_from_directory``.

    This function is idempotent – it returns immediately if prepared data
    already exists.

    Raises
    ------
    FileNotFoundError
        If the raw archive / folder has not been placed in the expected location.
    """
    if name not in DATASET_SPECS:
        raise ValueError(f"Unknown dataset '{name}'. Available: {list(DATASET_SPECS)}")

    spec = DATASET_SPECS[name]
    prepared = BASE_DATA_DIR / name / "prepared"

    if prepared.is_dir() and any(prepared.iterdir()):
        print(f"[{name}] Prepared data already exists at {prepared}")
        return prepared

    # Determine raw root — prefer already-extracted folder, fall back to zip
    raw: pathlib.Path | None = None

    local_raw: pathlib.Path | None = spec.get("local_raw")
    local_zip: pathlib.Path | None = spec.get("local_zip")

    if local_raw and local_raw.is_dir() and any(f.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp"} for f in local_raw.rglob("*") if f.is_file()):
        # Already extracted (e.g. via kaggle --unzip)
        raw = local_raw
        print(f"[{name}] Found pre-extracted data at {raw}")
    elif local_zip and local_zip.is_file():
        # Extract the zip
        raw = _extract_zip(local_zip, BASE_DATA_DIR / name / "raw")
    else:
        paths_tried = [str(p) for p in [local_raw, local_zip] if p]
        raise FileNotFoundError(
            f"\n[{name}] Dataset not found. Tried:\n"
            + "\n".join(f"  {p}" for p in paths_tried)
            + f"\n\nDownload from: {spec['description']}\n"
            "Then re-run the training script."
        )

    print(f"[{name}] Organising images into class folders ...")
    _flatten_folder_structure(raw, prepared, spec["class_source"])
    print(f"[{name}] Done -> {prepared}")
    return prepared


def load_tf_dataset(
    name: str,
    batch_size: int = 32,
    img_size: tuple = (224, 224),
    validation_split: float = 0.2,
    seed: int = 42,
) -> tuple:
    """Return ``(train_ds, val_ds, class_names)`` ready for ``model.fit()``.

    Both datasets include normalisation to [0, 1]. The training set also
    applies random horizontal flip, small rotation, and zoom augmentation.
    """
    prepared = prepare_dataset(name)

    train_ds = tf.keras.utils.image_dataset_from_directory(
        prepared,
        label_mode="int",
        image_size=img_size,
        batch_size=batch_size,
        shuffle=True,
        validation_split=validation_split,
        subset="training",
        seed=seed,
    )
    # IMPORTANT: use the SAME shuffle + seed as the training subset. With
    # validation_split, Keras shuffles the file list before slicing only when
    # shuffle=True; passing shuffle=False here made the validation subset the
    # last 20% of the class-ordered file list (i.e. only the alphabetically-last
    # classes), so train/val did not partition consistently.
    val_ds = tf.keras.utils.image_dataset_from_directory(
        prepared,
        label_mode="int",
        image_size=img_size,
        batch_size=batch_size,
        shuffle=True,
        validation_split=validation_split,
        subset="validation",
        seed=seed,
    )
    class_names = train_ds.class_names

    # Normalise to [0, 1]
    rescale = tf.keras.layers.Rescaling(1.0 / 255)

    # Training augmentation. NOTE: augmentation runs *after* the Rescaling to
    # [0, 1], so RandomBrightness must use value_range=(0, 1) — the default
    # (0, 255) would add deltas up to ~25 and clip, destroying every image.
    augment = tf.keras.Sequential([
        tf.keras.layers.RandomFlip("horizontal"),
        tf.keras.layers.RandomRotation(0.1),
        tf.keras.layers.RandomZoom(0.1),
        tf.keras.layers.RandomBrightness(0.1, value_range=(0, 1)),
    ])

    train_ds = (
        train_ds
        .map(lambda x, y: (rescale(x), y), num_parallel_calls=tf.data.AUTOTUNE)
        .map(lambda x, y: (augment(x, training=True), y), num_parallel_calls=tf.data.AUTOTUNE)
        .prefetch(tf.data.AUTOTUNE)
    )
    val_ds = (
        val_ds
        .map(lambda x, y: (rescale(x), y), num_parallel_calls=tf.data.AUTOTUNE)
        .prefetch(tf.data.AUTOTUNE)
    )

    return train_ds, val_ds, class_names


if __name__ == "__main__":
    for d in DATASET_SPECS:
        try:
            path = prepare_dataset(d)
            print(f"Dataset '{d}' ready at {path}")
        except FileNotFoundError as e:
            print(e)
