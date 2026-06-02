"""Human-in-the-loop review actions for staff."""
from src.db.repository import (
    approve_interaction, reject_interaction, get_pending_reviews, update_case, get_interaction,
)
from src.i18n.language import apply_farmer_language, pending_message, normalize_language


def list_pending_for_review() -> list[dict]:
    return get_pending_reviews()


def staff_approve(interaction_id: int, final_text: str, reviewer: str, case_id: int | None = None) -> None:
    row = get_interaction(interaction_id) or {}
    lang = normalize_language(row.get("language"))
    farmer_text = apply_farmer_language(final_text, lang)
    approve_interaction(interaction_id, farmer_text, reviewer)
    if case_id:
        update_case(case_id, status="resolved", review_status="approved", follow_up_notes="Approved by staff")


def staff_reject(interaction_id: int, reviewer: str, case_id: int | None = None) -> None:
    row = get_interaction(interaction_id) or {}
    lang = normalize_language(row.get("language"))
    note = pending_message(lang).replace("approved", "follow up")
    reject_interaction(interaction_id, reviewer, note=apply_farmer_language(
        "A GreenHarvest field officer will contact you or visit your farm for this case.",
        lang,
    ))
    if case_id:
        update_case(case_id, status="resolved", review_status="rejected")
