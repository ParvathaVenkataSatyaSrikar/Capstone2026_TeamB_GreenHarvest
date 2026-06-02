"""LangChain chat models — Gemini with offline fallback."""
from langchain_core.language_models.chat_models import BaseChatModel

from src.resilience.llm_router import (
    get_resilient_chat_model,
    get_last_provider,
    get_primary_chat_model,
    probe_providers,
)


def get_chat_model() -> BaseChatModel:
    """Resilient wrapper for LCEL chains (prompt | llm | parser)."""
    return get_resilient_chat_model()


def get_structured_chat_model() -> BaseChatModel | None:
    """Online LLM for with_structured_output (Pydantic schemas)."""
    return get_primary_chat_model()
