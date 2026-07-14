# backend/utils/prepare_domain_gate.py
"""Assemble the 3-class ``domain_gate`` dataset used to validate uploads.

The gate model answers one question per predict endpoint:
    "Is this image actually a skin photo?"  /  "Is this actually a leaf photo?"
It has classes ``skin``, ``leaf``, ``other``.

``skin`` and ``leaf`` are seeded from the already-prepared diagnosis datasets
(``data/skin_disease/prepared`` and ``data/medicinal_leaves/prepared``). The
``other`` class should be supplied by you: drop ~300+ non-skin, non-leaf images
(objects, scenery, animals, food, screenshots, text) into
``data/domain_gate/raw_other/``.

If ``raw_other`` is empty, we generate a diverse synthetic ``other`` set fully
offline (gradients, textures, objects, scenes, text) — no downloads. These are
proxies and NOT a substitute for real photos; replace ``raw_other`` with real
images and re-run for production accuracy.

Run:
    python -m utils.prepare_domain_gate
"""

import pathlib
import random
import shutil

# Always resolve relative to backend/ regardless of CWD.
_BACKEND_DIR = pathlib.Path(__file__).resolve().parent.parent
BASE_DATA_DIR = _BACKEND_DIR / "data"
GATE_DIR = BASE_DATA_DIR / "domain_gate"
PREPARED = GATE_DIR / "prepared"
RAW_OTHER = GATE_DIR / "raw_other"

# Sources for the in-domain classes (reuse the diagnosis datasets' prepared images).
SKIN_SOURCE = BASE_DATA_DIR / "skin_disease" / "prepared"
LEAF_SOURCE = BASE_DATA_DIR / "medicinal_leaves" / "prepared"

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

# Target number of images per in-domain class *group* (so skin/leaf/other stay balanced).
TARGET_PER_GROUP = 2500
MIN_OTHER_IMAGES = 300

_random = random.Random(42)


def _is_image(p: pathlib.Path) -> bool:
    return p.is_file() and p.suffix.lower() in IMAGE_SUFFIXES


def _copy_sample(
    src_class_dir: pathlib.Path, dest_class_dir: pathlib.Path, cap: int
) -> int:
    dest_class_dir.mkdir(parents=True, exist_ok=True)
    images = [p for p in src_class_dir.rglob("*") if _is_image(p)]
    _random.shuffle(images)
    copied = 0
    for src in images[:cap]:
        dest = dest_class_dir / src.name
        n = 1
        while dest.exists():
            dest = dest_class_dir / f"{src.stem}_{n}{src.suffix}"
            n += 1
        shutil.copy2(src, dest)
        copied += 1
    return copied


def _copy_all(src_dir: pathlib.Path, dest_class_dir: pathlib.Path) -> int:
    dest_class_dir.mkdir(parents=True, exist_ok=True)
    images = [p for p in src_dir.rglob("*") if _is_image(p)]
    for src in images:
        dest = dest_class_dir / src.name
        n = 1
        while dest.exists():
            dest = dest_class_dir / f"{src.stem}_{n}{src.suffix}"
            n += 1
        shutil.copy2(src, dest)
    return len(images)


def _generate_synthetic_other(
    dest: pathlib.Path, count: int = 3000, size: int = 224
) -> int:
    """Generate a diverse, fully-offline 'other' set (no downloads).

    Produces photo-like variety covering the semantics a user might wrongly
    upload: color/gradient backgrounds, structured textures (wood, fabric, fur,
    stone, food), geometric 'objects', text/document shots, and simple scenes.
    Some skin-tone and green patches are included on purpose so the gate learns
    *structure*, not just hue. These are proxies — replace with real photos for
    production accuracy.
    """
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    import numpy as np

    rng = np.random.default_rng(7)
    dest.mkdir(parents=True, exist_ok=True)

    def smooth_noise(blur):
        base = rng.integers(0, 256, (size, size, 3), dtype=np.uint8)
        im = Image.fromarray(base).filter(ImageFilter.GaussianBlur(int(blur)))
        return np.asarray(im, dtype=np.float32)

    def tint(rgb):
        # multiply a gray-ish texture by a random color palette
        color = rng.integers(60, 256, 3).astype(np.float32)
        return np.clip(rgb * (color / 255.0), 0, 255).astype(np.uint8)

    font = ImageFont.load_default()
    made = 0
    kinds = ["texture", "gradient", "object", "scene", "text", "mixed"]
    while made < count:
        kind = kinds[made % len(kinds)]
        if kind == "texture":
            img = tint(smooth_noise(rng.choice([6, 14, 28])))
        elif kind == "gradient":
            c1 = rng.integers(0, 256, 3)
            c2 = rng.integers(0, 256, 3)
            t = np.linspace(0, 1, size)[:, None, None]
            img = (c1 * (1 - t) + c2 * t).astype(np.uint8).repeat(size, axis=1)
        elif kind == "object":
            bg = tint(smooth_noise(20))
            layer = Image.fromarray(bg)
            d = ImageDraw.Draw(layer)
            for _ in range(rng.integers(1, 5)):
                col = tuple(int(x) for x in rng.integers(0, 256, 3))
                xa, ya = rng.integers(0, size, 2)
                xb, yb = rng.integers(0, size, 2)
                x0, x1 = int(min(xa, xb)), int(max(xa, xb))
                y0, y1 = int(min(ya, yb)), int(max(ya, yb))
                d.ellipse([x0, y0, x1, y1], fill=col)
                d.rectangle(
                    [x0, y0, x1, y1], outline=col, width=int(rng.integers(2, 8))
                )
            img = np.asarray(layer)
        elif kind == "scene":
            sky = rng.integers(120, 230, 3)
            ground = rng.integers(60, 180, 3)
            horizon = int(rng.integers(size // 3, 2 * size // 3))
            img = np.zeros((size, size, 3), np.uint8)
            img[:horizon] = sky
            img[horizon:] = ground
            # a few "building" rectangles on the ground
            for _ in range(rng.integers(2, 7)):
                bx = int(rng.integers(0, size))
                bw = int(rng.integers(20, 80))
                bh = int(rng.integers(20, horizon))
                img[horizon - bh : horizon, max(0, bx) : min(size, bx + bw)] = tuple(
                    int(x) for x in rng.integers(80, 200, 3)
                )
        elif kind == "text":
            img = np.full((size, size, 3), 245, np.uint8)
            layer = Image.fromarray(img)
            d = ImageDraw.Draw(layer)
            for _ in range(rng.integers(4, 12)):
                y = int(rng.integers(0, size - 12))
                x = int(rng.integers(0, size // 2))
                txt = "".join(
                    rng.choice(list("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"))
                    for _ in range(rng.integers(4, 12))
                )
                d.text(
                    (x, y),
                    txt,
                    fill=tuple(int(v) for v in rng.integers(0, 120, 3)),
                    font=font,
                )
            img = np.asarray(layer)
        else:  # mixed
            a = tint(smooth_noise(int(rng.choice([8, 20]))))
            b = (rng.integers(0, 256, 3) * np.ones((size, size, 3))).astype(np.uint8)
            img = np.clip(a * 0.6 + b.astype(np.float32) * 0.4, 0, 255).astype(np.uint8)
            # occasional skin-tone / green patch to avoid hue-only shortcuts
            if rng.random() < 0.4:
                layer = Image.fromarray(img)
                d = ImageDraw.Draw(layer)
                col = (
                    tuple(int(v) for v in rng.integers(180, 240, 3))
                    if rng.random() < 0.5
                    else (
                        int(rng.integers(20, 90)),
                        int(rng.integers(120, 200)),
                        int(rng.integers(40, 110)),
                    )
                )
                d.ellipse(
                    [
                        int(rng.integers(0, size // 2)),
                        int(rng.integers(0, size // 2)),
                        int(rng.integers(size // 2, size)),
                        int(rng.integers(size // 2, size)),
                    ],
                    fill=col,
                )
                img = np.asarray(layer)

        Image.fromarray(img).save(dest / f"other_{made:05d}.png")
        made += 1
    print(f"[domain_gate] Generated {made} synthetic 'other' images (offline).")
    return made


def prepare_domain_gate() -> pathlib.Path:
    if not SKIN_SOURCE.is_dir() or not any(SKIN_SOURCE.iterdir()):
        raise FileNotFoundError(
            f"Skin source not found: {SKIN_SOURCE}\n"
            "Run `python -m utils.merge_skin_datasets` / train the skin model first."
        )
    if not LEAF_SOURCE.is_dir() or not any(LEAF_SOURCE.iterdir()):
        raise FileNotFoundError(f"Leaf source not found: {LEAF_SOURCE}")

    # 'other' is supplied by the user; if too few images are present (or only a
    # stale proxy remains), generate a synthetic proxy set fully offline (no
    # downloads). These stand-ins are NOT a substitute for real photos — replace
    # raw_other with real images and re-run for production accuracy.
    existing_other = (
        [p for p in RAW_OTHER.rglob("*") if _is_image(p)] if RAW_OTHER.is_dir() else []
    )
    if len(existing_other) < MIN_OTHER_IMAGES:
        if existing_other:
            print(
                f"[domain_gate] Found only {len(existing_other)} 'other' images "
                "(stale/insufficient) -> clearing and regenerating."
            )
            for p in existing_other:
                try:
                    p.unlink()
                except OSError:
                    pass
        print(
            "[domain_gate] 'other' class empty -> generating a synthetic proxy set "
            "(offline). Replace with real photos for production accuracy."
        )
        other_total = _generate_synthetic_other(RAW_OTHER)
        if other_total < MIN_OTHER_IMAGES:
            raise SystemExit(
                f"[domain_gate] Only generated {other_total} 'other' images "
                f"(need >= {MIN_OTHER_IMAGES})."
            )
    else:
        other_total = len(existing_other)

    # Clear any previous prepared layout so re-runs stay idempotent.
    if PREPARED.is_dir():
        shutil.rmtree(PREPARED)

    skin_classes = [d for d in sorted(SKIN_SOURCE.iterdir()) if d.is_dir()]
    leaf_classes = [d for d in sorted(LEAF_SOURCE.iterdir()) if d.is_dir()]
    skin_cap = max(5, TARGET_PER_GROUP // max(1, len(skin_classes)))
    leaf_cap = max(5, TARGET_PER_GROUP // max(1, len(leaf_classes)))

    skin_total = sum(_copy_sample(c, PREPARED / "skin", skin_cap) for c in skin_classes)
    leaf_total = sum(_copy_sample(c, PREPARED / "leaf", leaf_cap) for c in leaf_classes)
    copied_other = _copy_all(RAW_OTHER, PREPARED / "other")

    print(
        f"[domain_gate] Prepared -> {PREPARED}\n"
        f"  skin : {skin_total} images\n"
        f"  leaf : {leaf_total} images\n"
        f"  other: {copied_other} images"
    )
    return PREPARED


if __name__ == "__main__":
    prepare_domain_gate()
