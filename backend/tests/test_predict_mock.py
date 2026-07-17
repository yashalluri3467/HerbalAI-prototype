"""Offline smoke tests for the prediction endpoints.

The real TensorFlow model + OpenRouter LLM are monkeypatched out so the
tests run fast and without network/model weights. We only assert the
request/response contract and the domain-gate rejection path.
"""

import pytest
from fastapi.testclient import TestClient

import main


def _fake_predict(name: str, contents: bytes, img_size=None):
    return {
        "predicted_class": "test_class",
        "confidence": 0.95,
        "all_probs": {"test_class": 0.95, "other": 0.05},
        "quality": {
            "is_uncertain": False,
            "top_confidence": 0.95,
            "margin": 0.9,
            "normalized_entropy": 0.1,
        },
    }


def _fake_predict_healthy(name: str, contents: bytes, img_size=None):
    return {
        "predicted_class": "unknown_normal",
        "confidence": 0.80,
        "all_probs": {"unknown_normal": 0.80, "acne": 0.05},
        "quality": {
            "is_uncertain": False,
            "top_confidence": 0.80,
            "margin": 0.75,
            "normalized_entropy": 0.1,
        },
    }


def _fake_predict_uncertain(name: str, contents: bytes, img_size=None):
    return {
        "predicted_class": "acne",
        "confidence": 0.30,
        "all_probs": {"acne": 0.30, "eczema": 0.28},
        "quality": {
            "is_uncertain": True,
            "top_confidence": 0.30,
            "margin": 0.02,
            "normalized_entropy": 0.95,
        },
    }


@pytest.fixture
def disable_optional_paths():
    """Turn off knowledge-base + LLM so the test stays offline/fast."""
    saved = (
        main.app_settings.knowledge_base_enabled,
        main.app_settings.llm_suggestions_enabled,
    )
    main.app_settings.knowledge_base_enabled = False
    main.app_settings.llm_suggestions_enabled = False
    yield
    (
        main.app_settings.knowledge_base_enabled,
        main.app_settings.llm_suggestions_enabled,
    ) = saved


def test_predict_skin_success(monkeypatch, disable_optional_paths):
    monkeypatch.setattr(main, "is_valid_domain", lambda *a, **k: True)
    monkeypatch.setattr(main, "tf_predict", _fake_predict)
    # Stub the real cv2 decode / base64 encode so the test stays offline.
    monkeypatch.setattr(main, "process_image", lambda c: (None, None))
    monkeypatch.setattr(
        main, "image_to_base64", lambda img: "data:image/jpeg;base64,STUB"
    )

    client = TestClient(main.app)
    response = client.post(
        "/api/predict/skin",
        files={"file": ("skin.jpg", b"dummy-bytes", "image/jpeg")},
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["disease"] == "Test Class"
    assert body["is_healthy"] is False
    assert body["classification_status"] == "classified"
    assert "confidence_score" in body
    assert "top_predictions" in body


def test_predict_skin_healthy_class(monkeypatch, disable_optional_paths):
    monkeypatch.setattr(main, "is_valid_domain", lambda *a, **k: True)
    monkeypatch.setattr(main, "tf_predict", _fake_predict_healthy)
    monkeypatch.setattr(main, "process_image", lambda c: (None, None))
    monkeypatch.setattr(
        main, "image_to_base64", lambda img: "data:image/jpeg;base64,STUB"
    )

    client = TestClient(main.app)
    response = client.post(
        "/api/predict/skin",
        files={"file": ("skin.jpg", b"dummy-bytes", "image/jpeg")},
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["disease"] == "Healthy Skin"
    assert body["is_healthy"] is True
    assert body["classification_status"] == "healthy"
    assert body["recommendations"] == []


def test_predict_skin_uncertain_is_healthy(monkeypatch, disable_optional_paths):
    monkeypatch.setattr(main, "is_valid_domain", lambda *a, **k: True)
    monkeypatch.setattr(main, "tf_predict", _fake_predict_uncertain)
    monkeypatch.setattr(main, "process_image", lambda c: (None, None))
    monkeypatch.setattr(
        main, "image_to_base64", lambda img: "data:image/jpeg;base64,STUB"
    )

    client = TestClient(main.app)
    response = client.post(
        "/api/predict/skin",
        files={"file": ("skin.jpg", b"dummy-bytes", "image/jpeg")},
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["disease"] == "Healthy Skin"
    assert body["is_healthy"] is True
    assert body["classification_status"] == "healthy"


def test_predict_skin_domain_rejected(monkeypatch):
    monkeypatch.setattr(main, "is_valid_domain", lambda *a, **k: False)

    client = TestClient(main.app)
    response = client.post(
        "/api/predict/skin",
        files={"file": ("x.jpg", b"dummy", "image/jpeg")},
    )

    assert response.status_code == 422
