"""Application configuration from environment variables."""
import os
from pathlib import Path
from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parent.parent


def _load_env_file() -> None:
    """Load .env into os.environ (handles spaces/quotes around values)."""
    env_path = ROOT_DIR / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, val = line.split("=", 1)
        val = val.strip().strip('"').strip("'")
        if val:
            os.environ.setdefault(key.strip(), val)

DATA_DIR = ROOT_DIR / "data"
KB_DIR = ROOT_DIR / "knowledge_base"
FAISS_DIR = DATA_DIR / "faiss_index"
DB_PATH = DATA_DIR / "greenharvest.db"
TESTS_DIR = ROOT_DIR / "tests"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ROOT_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash-lite"
    gemini_vision_model: str = "gemini-2.5-flash"
    openai_vision_model: str = "gpt-4o-mini"
    llm_provider: str = "auto"  # auto = OpenAI first, then Gemini, then offline RAG
    llm_request_timeout_sec: int = 35
    staff_demo_password: str = "greenharvest2026"
    retrieval_min_score: float = 0.35
    escalation_confidence_threshold: float = 0.55
    gemini_embedding_model: str = "models/gemini-embedding-001"
    tavily_api_key: str = ""
    skip_llm_intake_when_keywords: bool = True

    @field_validator(
        "openai_api_key", "gemini_api_key", "tavily_api_key", mode="before",
    )
    @classmethod
    def strip_quotes(cls, v):
        if isinstance(v, str):
            return v.strip().strip('"').strip("'")
        return v or ""


@lru_cache
def get_settings() -> Settings:
    _load_env_file()
    return Settings()
