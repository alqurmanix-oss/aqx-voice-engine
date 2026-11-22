from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class Transcription:
    text: str
    language: str | None = None
    language_probability: float | None = None

class STTAdapter(ABC):
    @abstractmethod
    def transcribe(self, audio_path: str, language: str | None = None) -> Transcription:
        raise NotImplementedError

class TTSAdapter(ABC):
    @abstractmethod
    def synthesize(self, text: str, language: str, voice: str | None = None) -> bytes:
        raise NotImplementedError
