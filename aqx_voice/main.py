import hmac
import logging
from pathlib import Path

from fastapi import Depends, FastAPI, File, Header, HTTPException, UploadFile
from pydantic import BaseModel, Field

from aqx_voice.config import settings
from aqx_voice.registry import load_registry

logging.basicConfig(level=settings.log_level)
app = FastAPI(title="AQX Voice Engine", version="0.1.0")

def require_api_key(x_aqx_api_key: str | None = Header(default=None)):
    if settings.aqx_env == "production" and settings.aqx_api_key == "change-me":
        raise HTTPException(status_code=503, detail="Server API key is not configured")
    if not x_aqx_api_key or not hmac.compare_digest(x_aqx_api_key, settings.aqx_api_key):
        raise HTTPException(status_code=401, detail="Invalid API key")

class SpeakRequest(BaseModel):
    text: str = Field(min_length=1)
    language: str = Field(min_length=2, max_length=35)
    voice: str | None = None

@app.get("/health")
def health():
    return {"status": "healthy", "service": "aqx-voice-engine", "inference_ready": False}

@app.get("/v1/capabilities", dependencies=[Depends(require_api_key)])
def capabilities():
    registry = load_registry()
    return {
        "tts": {"configured": settings.tts_adapter != "none", "adapter": settings.tts_adapter},
        "stt": {"configured": settings.stt_adapter != "none", "adapter": settings.stt_adapter},
        "models": registry.get("models", []),
        "note": "Only locally validated models count as verified language support."
    }

@app.post("/v1/tts", dependencies=[Depends(require_api_key)])
def tts(request: SpeakRequest):
    if len(request.text) > settings.max_text_chars:
        raise HTTPException(status_code=413, detail="Text exceeds configured limit")
    raise HTTPException(status_code=503, detail="No local TTS adapter is installed and validated")

@app.post("/v1/stt", dependencies=[Depends(require_api_key)])
async def stt(file: UploadFile = File(...), language: str | None = None):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing filename")
    data = await file.read(settings.max_upload_mb * 1024 * 1024 + 1)
    if len(data) > settings.max_upload_mb * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Audio file exceeds configured limit")
    raise HTTPException(status_code=503, detail="No local STT adapter is installed and validated")
