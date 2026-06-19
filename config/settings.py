from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Kernel Karl LLM"
    app_version: str = "1.0.0"
    backend: str = "llama_cpp"
    log_level: str = "INFO"

    model_path: Path = Path("/models/qwen3-14b-instruct-q4_k_m.gguf")
    model_context: int = Field(default=8192, ge=512)
    model_threads: int = Field(default=8, ge=0)
    model_gpu_layers: int = Field(default=0, ge=0)

    default_temperature: float = Field(default=0.2, ge=0.0, le=2.0)
    default_max_tokens: int = Field(default=800, ge=1)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
