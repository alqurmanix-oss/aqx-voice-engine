from fastapi.testclient import TestClient
from aqx_voice.main import app

client = TestClient(app)
AUTH = {"X-AQX-API-Key": "change-me"}

def test_health_does_not_claim_inference_ready():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["inference_ready"] is False

def test_auth_required_for_capabilities():
    assert client.get("/v1/capabilities").status_code == 401

def test_tts_fails_closed_without_local_adapter():
    response = client.post(
        "/v1/tts",
        headers=AUTH,
        json={"text": "مرحبا", "language": "ar-EG"},
    )
    assert response.status_code == 503

def test_stt_fails_closed_when_adapter_disabled():
    response = client.post(
        "/v1/stt",
        headers=AUTH,
        files={"file": ("sample.wav", b"fake-audio", "audio/wav")},
    )
    assert response.status_code == 503

def test_stt_rejects_unsupported_extension():
    response = client.post(
        "/v1/stt",
        headers=AUTH,
        files={"file": ("payload.exe", b"not-audio", "application/octet-stream")},
    )
    assert response.status_code == 415
