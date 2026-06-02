"""Plain-language labels and review explanations for farmers (no backend jargon)."""
from src.ui.brand import GH

INTENT_LABELS = {
    "pest_disease": "Pest or disease",
    "crop_advisory": "Crop care",
    "irrigation": "Irrigation",
    "input_recommendation": "Fertilizer & inputs",
    "market_price": "Market price",
    "insurance": "Crop insurance",
    "scheme_information": "Government scheme",
    "escalation": "Urgent help",
}

REVIEW_EXPLAIN = {
    "auto_approved": {
        "title": "Instant answer",
        "icon": "✅",
        "summary": "Your answer was shared immediately.",
        "detail": "This looked like a routine question where our guides and your farm details were enough to answer safely.",
    },
    "pending_human": {
        "title": "With agriculture expert",
        "icon": "⏳",
        "summary": "A field officer will review before you see the full advice.",
        "detail": "We do this when the topic needs extra care — for example pests, insurance, low confidence, or urgent words in your question.",
    },
    "approved": {
        "title": "Expert approved",
        "icon": "✅",
        "summary": "A GreenHarvest officer checked and approved this answer.",
        "detail": "You can follow this guidance with more confidence.",
    },
    "rejected": {
        "title": "Officer follow-up",
        "icon": "📞",
        "summary": "An officer will contact you or visit the field.",
        "detail": "The AI could not give safe automated advice for this case.",
    },
}


def friendly_intent(intent: str) -> str:
    return INTENT_LABELS.get(intent, intent.replace("_", " ").title() if intent else "General")


def explain_escalation_reason(raw: str) -> str:
    """Turn backend reason codes into farmer-friendly text."""
    if not raw:
        return "Your question needs a human expert to double-check before we share full advice."
    parts = []
    for token in raw.replace(",", " ").split():
        t = token.strip().lower()
        if t == "low_confidence":
            parts.append("the system was not fully sure about the best answer")
        elif t.startswith("intent_"):
            topic = t.replace("intent_", "").replace("_", " ")
            parts.append(f"it is about {topic}, which needs expert care")
        elif t.startswith("keyword_"):
            parts.append("your message sounds urgent or serious")
        elif t:
            parts.append(t.replace("_", " "))
    if not parts:
        return "This topic needs expert review for your safety."
    return "Sent for review because " + ", and ".join(parts) + "."


def review_card_html(status: str, escalation_reason: str = "", confidence: float | None = None) -> str:
    info = REVIEW_EXPLAIN.get(status, REVIEW_EXPLAIN["auto_approved"])
    extra = ""
    if status == "pending_human":
        extra = (
            f'<p style="margin:0.5rem 0 0;font-size:0.88rem;color:{GH["warning"]};">'
            f"{explain_escalation_reason(escalation_reason)}</p>"
        )
    elif status == "auto_approved" and confidence is not None:
        extra = (
            f'<p style="margin:0.5rem 0 0;font-size:0.88rem;color:{GH["muted"]};">'
            f"Routine query — no expert review needed.</p>"
        )
    border = GH["warning_border"] if status == "pending_human" else GH["success_border"]
    bg = GH["warning_bg"] if status == "pending_human" else GH["success_bg"]
    return (
        f'<div style="background:{bg};border:1px solid {border};border-radius:12px;'
        f'padding:0.85rem 1rem;margin:0.75rem 0;">'
        f'<strong style="color:{GH["crop_primary"]};">{info["icon"]} {info["title"]}</strong>'
        f'<p style="margin:0.35rem 0 0;font-size:0.9rem;color:{GH["text"]};">{info["summary"]}</p>'
        f"{extra}</div>"
    )


def render_review_status(status: str, escalation_reason: str = "", confidence: float | None = None) -> None:
    import streamlit as st

    st.markdown(review_card_html(status, escalation_reason, confidence), unsafe_allow_html=True)
