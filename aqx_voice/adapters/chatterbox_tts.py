import io
import os
import re
import threading
from pathlib import Path

import soundfile as sf

from aqx_voice.adapters.base import TTSAdapter
from aqx_voice.config import settings

SUPPORTED_LANGUAGES = {
    "ar", "da", "de", "el", "en", "es", "fi", "fr", "he", "hi", "it",
    "ja", "ko", "ms", "nl", "no", "pl", "pt", "ru", "sv", "sw", "tr", "zh",
}

class ChatterboxMultilingualTTS(TTSAdapter):
    """Local Chatterbox multilingual V3 adapter. Hugging Face networking is disabled."""

    def __init__(self) -> None:
        os.environ["HF_HUB_OFFLINE"] = "1"
        os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
        self.voice_dir = Path(settings.tts_voice_dir).resolve()
        self.voice_dir.mkdir(parents=True, exist_ok=True)
        from chatterbox.mtl_tts import ChatterboxMultilingualTTS as ChatterboxModel
        self.model = ChatterboxModel.from_pretrained(
            device=settings.tts_device,
            t3_model="v3",
        )
        self._lock = threading.Lock()

    def synthesize(self, text: str, language: str, voice: str | None = None) -> bytes:
        language_id = language.lower().split("-", 1)[0].split("_", 1)[0]
        if language_id not in SUPPORTED_LANGUAGES:
            raise ValueError(f"Unsupported Chatterbox language code: {language_id}")

        kwargs = {"language_id": language_id}
        if voice:
            if not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", voice):
                raise ValueError("Voice must be a registered voice ID")
            voice_path = (self.voice_dir / f"{voice}.wav").resolve()
            if voice_path.parent != self.voice_dir or not voice_path.is_file():
                raise ValueError(f"Registered voice not found: {voice}")
            kwargs["audio_prompt_path"] = str(voice_path)

        with self._lock:
            audio = self.model.generate(text, **kwargs)
        audio_array = audio.squeeze(0).detach().cpu().numpy()
        output = io.BytesIO()
        sf.write(output, audio_array, self.model.sr, format="WAV")
        return output.getvalue()
