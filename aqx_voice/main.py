import hmac
import logging
import tempfile
from pathlib import Path

from fastapi import Depends, FastAPI, File, Header, HTTPException, UploadFile
from pydantic import BaseModel, Field

from aqx_voice.config import settings
from aqx_voice.registry import load_registry

logging.basicConfig(level=settings.log_level)
app = FastAPI(title="AQX Voice Engine", version="0.2.0")
_stt_instance = None

def require_api_key(x_aqx_api_key: str | None = Header(default=None)):
    if settings.aqx_env == "production" and settings.aqx_api_key == "change-me":
        raise HTTPException(status_code=503, detail="Server API key is not configured")
    if not x_aqx_api_key or not hmac.compare_digest(x_aqx_api_key, settings.aqx_api_key):
        raise HTTPException(status_code=401, detail="Invalid API key")

def get_stt_adapter():
    global _stt_instance
    if settings.stt_adapter == "none":
        raise HTTPException(status_code=503, detail="Local STT adapter is disabled")
    if settings.stt_adapter != "faster-whisper":
        raise HTTPException(status_code=503, detail="Unknown local STT adapter")
    if _stt_instance is None:
        try:
            from aqx_voice.adapters.faster_whisper_stt import FasterWhisperSTT
            _stt_instance = FasterWhisperSTT()
        except (ImportError, FileNotFoundError, OSError) as exc:
            logging.getLogger("aqx.voice").exception("Unable to initialize local STT")
            raise HTTPException(status_code=503, detail=f"Local STT is not ready: {exc}") from exc
    return _stt_instance

class SpeakRequest(BaseModel):
    text: str = Field(min_length=1)
    language: str = Field(min_length=2, max_length=35)
    voice: str | None = None

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "aqx-voice-engine",
        "inference_ready": False,
        "stt_configured": settings.stt_adapter != "none",
        "tts_configured": settings.tts_adapter != "none",
    }

@app.get("/v1/capabilities", dependencies=[Depends(require_api_key)])
def capabilities():
    registry = load_registry()
    model_dir = Path(settings.stt_model_path)
    return {
        "tts": {"configured": settings.tts_adapter != "none", "adapter": settings.tts_adapter},
        "stt": {
            "configured": settings.stt_adapter != "none",
            "adapter": settings.stt_adapter,
            "local_model_present": model_dir.is_dir(),
            "model_path": str(model_dir),
            "language_detection": True,
        },
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
    suffix = Path(file.filename).suffix.lower()
    if suffix not in {".wav", ".mp3", ".m4a", ".flac", ".ogg", ".webm", ".mp4"}:
        raise HTTPException(status_code=415, detail="Unsupported audio file extension")
    data = await file.read(settings.max_upload_mb * 1024 * 1024 + 1)
    if not data:
        raise HTTPException(status_code=400, detail="Empty audio file")
    if len(data) > settings.max_upload_mb * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Audio file exceeds configured limit")

    adapter = get_stt_adapter()
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp_file:
            temp_file.write(data)
            temp_path = temp_file.name
        result = adapter.transcribe(temp_path, language=language)
        return {
            "text": result.text,
            "language": result.language,
            "language_probability": result.language_probability,
            "language_mode": "specified" if language else "auto-detected",
            "model": settings.stt_adapter,
        }
    finally:
        if temp_path:
            Path(temp_path).unlink(missing_ok=True)
