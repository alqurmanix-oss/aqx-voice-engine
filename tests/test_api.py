from fastapi.testclient import TestClient
from aqx_voice.main import app

client = TestClient(app)

def test_health_does_not_claim_inference_ready():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["inference_ready"] is False

def test_auth_required_for_capabilities():
    assert client.get("/v1/capabilities").status_code == 401

def test_tts_fails_closed_without_local_adapter():
    response = client.post(
        "/v1/tts",
        headers={"X-AQX-API-Key": "change-me"},
        json={"text": "مرحبا", "language": "ar-EG"},
    )
    assert response.status_code == 503
