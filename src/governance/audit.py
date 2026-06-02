"""Audit logging for governance."""
from config.settings import get_settings
from src.resilience.llm_router import get_last_provider
from src.db.repository import save_audit_log


def _model_label() -> str:
    provider = get_last_provider()
    if provider and provider != "unknown":
        return provider
    return get_settings().gemini_model


def log_pipeline_run(
    interaction_id: int | None,
    user_role: str,
    confidence: float,
    chunk_ids: list[str],
    guardrail_triggered: bool,
    details: dict,
) -> None:
    save_audit_log({
        "interaction_id": interaction_id,
        "user_role": user_role,
        "action": "pipeline_complete",
        "model_used": _model_label(),
        "chunk_ids": chunk_ids,
        "confidence": confidence,
        "guardrail_triggered": guardrail_triggered,
        "details": details,
    })
