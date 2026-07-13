# backend/utils/verify_domain_gate.py
"""Offline verification that the upload domain-gate model is trained and active.

Usage:
    python -m utils.verify_domain_gate

Expects a trained model at ``backend/models/domain_gate/`` (produced by
``train_tf_models --dataset domain_gate``). Builds a small in-memory report:

  * class set is exactly {skin, leaf, other}
  * in-domain images pass (skin image -> is_valid_domain("skin") is True, etc.)
  * off-domain images are rejected for BOTH skin and leaf

Exits non-zero if any check fails (handy for CI).
"""

import pathlib
import sys

import numpy as np

_BACKEND_DIR = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_BACKEND_DIR))

from services.domain_gate import is_valid_domain  # noqa: E402

DATA = _BACKEND_DIR / "data"
SKIN_DIR = DATA / "skin_disease" / "prepared"
LEAF_DIR = DATA / "medicinal_leaves" / "prepared"
OTHER_DIR = DATA / "domain_gate" / "prepared" / "other"


def _first_image(d: pathlib.Path) -> bytes:
    for p in sorted(d.rglob("*")):
        if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp", ".webp"}:
            return p.read_bytes()
    raise FileNotFoundError(f"No image found under {d}")


def main() -> int:
    failures = []

    # 1. Model must be present -> gate active.
    model_path = _BACKEND_DIR / "models" / "domain_gate" / "model.keras"
    if not model_path.is_file():
        print("FAIL: domain-gate model not found -> gate is DISABLED (always passes).")
        return 1
    print(f"OK:   model present at {model_path}")

    # 2. Class set check (order is alphabetical: leaf, other, skin).
    labels = (_BACKEND_DIR / "models" / "domain_gate" / "class_names.txt").read_text().split()
    if set(labels) != {"skin", "leaf", "other"}:
        failures.append(f"class set is {labels}, expected {{skin, leaf, other}}")
    else:
        print(f"OK:   classes = {labels}")

    # 3. In-domain passes, off-domain rejected.
    skin_bytes = _first_image(SKIN_DIR)
    leaf_bytes = _first_image(LEAF_DIR)
    other_bytes = _first_image(OTHER_DIR)

    checks = [
        ("skin image -> 'skin'", is_valid_domain("skin", skin_bytes), True),
        ("skin image -> 'leaf'", is_valid_domain("leaf", skin_bytes), False),
        ("leaf image -> 'leaf'", is_valid_domain("leaf", leaf_bytes), True),
        ("leaf image -> 'skin'", is_valid_domain("skin", leaf_bytes), False),
        ("other image -> 'skin'", is_valid_domain("skin", other_bytes), False),
        ("other image -> 'leaf'", is_valid_domain("leaf", other_bytes), False),
    ]
    for label, got, want in checks:
        ok = got == want
        print(f"{'OK  ' if ok else 'FAIL'} gate[{label}] = {got} (want {want})")
        if not ok:
            failures.append(label)

    if failures:
        print(f"\n{len(failures)} check(s) failed: {failures}")
        return 1
    print("\nAll domain-gate checks passed. Gate is active and behaving correctly.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
