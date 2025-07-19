from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    whisper_model_size: str = Field("small", env="WHISPER_MODEL_SIZE")
    whisper_device: str = Field("auto", env="WHISPER_DEVICE")
    whisper_compute_type: str = Field("auto", env="WHISPER_COMPUTE_TYPE")
    nllb_model: str = Field("facebook/nllb-200-distilled-600M", env="NLLB_MODEL")
    max_segment_chars: int = Field(90, env="MAX_SEGMENT_CHARS")
    max_line_chars: int = Field(42, env="MAX_LINE_CHARS")
    merge_gap_seconds: float = Field(0.4, env="MERGE_GAP_SECONDS")
    cache_dir: str = Field("cache", env="CACHE_DIR")
    download_dir: str = Field("downloads", env="DOWNLOAD_DIR")
    subs_dir: str = Field("subs", env="SUBS_DIR")
    audio_dir: str = Field("audio", env="AUDIO_DIR")

    class Config:
        env_file = ".env"

settings = Settings()

