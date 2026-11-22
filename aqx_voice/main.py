import hmac
import logging
import tempfile
import threading
from pathlib import Path

from fastapi import Depends, FastAPI, File, Header, HTTPException, UploadFile
from fastapi.responses import Response
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool

from aqx_voice.config import settings
from aqx_voice.registry import load_registry

logging.basicConfig(level=settings.log_level)
app = FastAPI(title="AQX Voice Engine", version="0.3.0")
_stt_instance = None
_tts_instance = None
_stt_init_lock = threading.Lock()
_tts_init_lock = threading.Lock()

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
        with _stt_init_lock:
            if _stt_instance is None:
                try:
                    from aqx_voice.adapters.faster_whisper_stt import FasterWhisperSTT
                    _stt_instance = FasterWhisperSTT()
                except Exception as exc:
                    logging.getLogger("aqx.voice").exception("Unable to initialize local STT")
                    raise HTTPException(status_code=503, detail=f"Local STT is not ready: {exc}") from exc
    return _stt_instance

def get_tts_adapter():
    global _tts_instance
    if settings.tts_adapter == "none":
        raise HTTPException(status_code=503, detail="Local TTS adapter is disabled")
    if settings.tts_adapter != "chatterbox":
        raise HTTPException(status_code=503, detail="Unknown local TTS adapter")
    if _tts_instance is None:
        with _tts_init_lock:
            if _tts_instance is None:
                try:
                    from aqx_voice.adapters.chatterbox_tts import ChatterboxMultilingualTTS
                    _tts_instance = ChatterboxMultilingualTTS()
                except Exception as exc:
                    logging.getLogger("aqx.voice").exception("Unable to initialize local TTS")
                    raise HTTPException(status_code=503, detail=f"Local TTS is not ready: {exc}") from exc
    return _tts_instance

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
    stt_dir = Path(settings.stt_model_path)
    return {
        "tts": {
            "configured": settings.tts_adapter != "none",
            "adapter": settings.tts_adapter,
            "voice_dir": settings.tts_voice_dir,
        },
        "stt": {
            "configured": settings.stt_adapter != "none",
            "adapter": settings.stt_adapter,
            "local_model_present": stt_dir.is_dir(),
            "model_path": str(stt_dir),
            "language_detection": settings.stt_adapter == "faster-whisper",
        },
        "models": registry.get("models", []),
        "note": "Only locally validated models count as verified language support."
    }

@app.post("/v1/tts", dependencies=[Depends(require_api_key)])
def tts(request: SpeakRequest):
    if len(request.text) > settings.max_text_chars:
        raise HTTPException(status_code=413, detail="Text exceeds configured limit")
    adapter = get_tts_adapter()
    try:
        audio = adapter.synthesize(request.text, request.language, request.voice)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        logging.getLogger("aqx.voice").exception("Local TTS inference failed")
        raise HTTPException(status_code=500, detail="Local TTS inference failed") from exc
    return Response(content=audio, media_type="audio/wav", headers={
        "Content-Disposition": 'attachment; filename="aqx-speech.wav"'
    })

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

    adapter = await run_in_threadpool(get_stt_adapter)
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp_file:
            temp_file.write(data)
            temp_path = temp_file.name
        result = await run_in_threadpool(adapter.transcribe, temp_path, language)
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
