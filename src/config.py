from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    voxtral_model: str = Field(
        "mistralai/Voxtral-Small-24B-2507", env="VOXTRAL_MODEL"
    )
    voxtral_device: str = Field("auto", env="VOXTRAL_DEVICE")
    mistral_model: str = Field(
        "mistralai/mistral-medium-2505", env="MISTRAL_MODEL"
    )
    mistral_device: str = Field("auto", env="MISTRAL_DEVICE")
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
