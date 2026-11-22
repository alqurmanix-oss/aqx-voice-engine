from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    aqx_env: str = "development"
    aqx_api_key: str = "change-me"
    model_dir: str = "/models"
    max_upload_mb: int = 25
    max_text_chars: int = 5000
    stt_adapter: str = "none"
    tts_adapter: str = "none"
    log_level: str = "INFO"

settings = Settings()
