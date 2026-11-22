from pathlib import Path

from aqx_voice.adapters.base import STTAdapter, Transcription
from aqx_voice.config import settings


class FasterWhisperSTT(STTAdapter):
    """Offline-only faster-whisper adapter. Accepts a local model directory, never a remote ID."""

    def __init__(self) -> None:
        self.model_path = Path(settings.stt_model_path).resolve()
        if not self.model_path.is_dir():
            raise FileNotFoundError(
                f"Local STT model directory not found: {self.model_path}. "
                "Provision model weights locally before enabling STT."
            )
        from faster_whisper import WhisperModel

        self.model = WhisperModel(
            str(self.model_path),
            device=settings.stt_device,
            compute_type=settings.stt_compute_type,
        )

    def transcribe(self, audio_path: str, language: str | None = None) -> Transcription:
        segments, info = self.model.transcribe(
            audio_path,
            language=language or None,
            vad_filter=True,
        )
        text = "".join(segment.text for segment in segments).strip()
        return Transcription(
            text=text,
            language=getattr(info, "language", None),
            language_probability=getattr(info, "language_probability", None),
        )
