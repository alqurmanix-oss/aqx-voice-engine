from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    aqx_env: str = "development"
    aqx_api_key: str = "change-me"
    model_dir: str = "/models"
    max_upload_mb: int = 25
    max_text_chars: int = 5000
    stt_adapter: str = "none"
    stt_model_path: str = "/models/whisper-large-v3"
    stt_device: str = "cpu"
    stt_compute_type: str = "int8"
    tts_adapter: str = "none"
    tts_device: str = "cpu"
    tts_voice_dir: str = "/models/voices"
    log_level: str = "INFO"

settings = Settings()
