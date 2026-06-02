"""Load and sync farmer chat from persisted interactions."""
from __future__ import annotations

from src.db.repository import get_interactions
from src.ui.trace_utils import escalation_from_row
from src.i18n.language import pending_message, normalize_language, get_session_language


def interactions_to_messages(rows: list[dict], language: str | None = None) -> list[dict]:
    lang = normalize_language(language or get_session_language())
    """Oldest-first chat messages from DB rows (newest interactions last)."""
    chronological = list(reversed(rows))
    messages: list[dict] = []
    for row in chronological:
        messages.append({
            "role": "user",
            "text": row.get("query_text") or "",
            "meta": {"interaction_id": row.get("interaction_id")},
        })
        status = row.get("review_status") or "auto_approved"
        if status == "pending_human":
            text = row.get("response_text") or pending_message(row.get("language") or lang)
        elif status == "rejected":
            text = row.get("response_text") or "An officer will follow up with you directly."
        else:
            text = row.get("response_text") or ""
        if not text.strip():
            text = "Answer recorded — open **My Queries** for details."
        messages.append({
            "role": "assistant",
            "text": text,
            "meta": {
                "review_status": status,
                "interaction_id": row.get("interaction_id"),
                "escalation_reason": escalation_from_row(row),
            },
        })
    return messages


def load_chat_from_db(farmer_id: str, limit: int = 12, language: str | None = None) -> list[dict]:
    rows = get_interactions(farmer_id=farmer_id, limit=limit)
    return interactions_to_messages(rows, language=language)
