"""Safe crop pipeline — never crash the UI; fall back to local knowledge base."""
from __future__ import annotations

import time

from src.rag.retriever import get_active_embedding_provider, retrieve
from src.i18n.language import apply_farmer_language, normalize_language, pending_message
from src.integrations.profile import get_profile
from src.integrations.query_focus import integration_focus


def _detect_market_query(lower: str) -> bool:
    return any(k in lower for k in ("mandi", "price", "market rate", "selling price", "today's price"))


def build_emergency_response(
    farmer_id: str,
    query: str,
    language: str,
    error_note: str = "",
) -> dict:
    """Keyword RAG + friendly message when LangGraph or APIs fail."""
    lang = normalize_language(language)
    crop = ""
    district = ""
    lower = query.lower()
    profile = get_profile(farmer_id) or {}
    district = profile.get("district", "")
    crop = profile.get("crop", "")
    for c in ["cotton", "paddy", "wheat", "tomato", "soybean", "rice", "maize", "chilli", "onion", "potato"]:
        if c in lower:
            crop = "paddy" if c == "rice" else c
            break

    focus = integration_focus(query)
    if focus:
        from src.integrations.market import format_market_answer
        from src.integrations.weather import format_weather_answer
        from src.integrations.soil import format_soil_answer
        from src.integrations.insurance_guide import format_insurance_answer

        parts = []
        if "insurance" in focus:
            parts.append(format_insurance_answer(farmer_id, district, crop, query=query))
        if "market" in focus:
            parts.append(format_market_answer(district, crop, language=lang))
        if "weather" in focus:
            parts.append(format_weather_answer(district, crop))
        if "soil" in focus:
            parts.append(format_soil_answer(farmer_id, district, crop))
        text = "\n\n".join(parts)
        if error_note:
            text += f"\n\n---\n*Note: {error_note}*"
        text = apply_farmer_language(text, lang)
        if "insurance" in focus:
            intent = "insurance"
        elif focus == {"market"}:
            intent = "market_price"
        elif "weather" in focus and "soil" not in focus:
            intent = "weather_advisory"
        elif "soil" in focus:
            intent = "soil_health"
        else:
            intent = "crop_advisory"
        return {
            "farmer_id": farmer_id,
            "query": query,
            "intent": intent,
            "intent_confidence": 0.85,
            "retrieval_confidence": 0.0,
            "model_confidence": 0.75,
            "final_confidence": 0.75,
            "escalated": False,
            "escalation_reason": "",
            "needs_human_review": False,
            "review_status": "auto_approved",
            "recommendation": text,
            "farmer_response": text,
            "draft_response": text,
            "staff_summary": f"Integration fallback — {farmer_id}: {query[:120]}",
            "safety_notes": "Demo CSV data — confirm locally before acting.",
            "citations": ["data/market_prices.csv", "data/weather.csv", "data/soil_reports.csv"],
            "retrieved_chunks": [],
            "guardrail_triggered": False,
            "agent_trace": {
                "fallback": {
                    "reason": error_note or "pipeline_error",
                    "store": get_active_embedding_provider(),
                    "mode": "integration_csv",
                }
            },
            "language": lang,
        }

    chunks = retrieve(query, crop=crop, top_k=3)
    if chunks:
        lines = []
        for i, ch in enumerate(chunks[:3], 1):
            snippet = ch["text"][:300].strip().replace("\n", " ")
            lines.append(f"{i}. {snippet}")
        body = "\n".join(lines)
        src = chunks[0].get("metadata", {}).get("source", "crop guide")
        text = (
            f"**Guidance from trusted guides** (backup mode)\n\n{body}\n\n"
            f"*Source: {src}. A field officer can confirm before you apply inputs.*"
        )
        confidence = 0.45
        review = "auto_approved"
    else:
        text = pending_message(lang) if "urgent" in lower or "emergency" in lower else (
            "**We received your question.**\n\n"
            "The AI service is temporarily unavailable. Your question is saved. "
            "Please try again in a few minutes or contact your nearest field officer."
        )
        confidence = 0.25
        review = "pending_human"

    if error_note:
        text += f"\n\n---\n*Note: {error_note}*"

    text = apply_farmer_language(text, lang)
    return {
        "farmer_id": farmer_id,
        "query": query,
        "intent": "crop_advisory",
        "intent_confidence": 0.5,
        "retrieval_confidence": 0.4 if chunks else 0.0,
        "model_confidence": confidence,
        "final_confidence": confidence,
        "escalated": review == "pending_human",
        "escalation_reason": "pipeline_fallback",
        "needs_human_review": review == "pending_human",
        "review_status": review,
        "recommendation": text,
        "farmer_response": text,
        "draft_response": text,
        "staff_summary": f"Fallback mode — farmer {farmer_id}: {query[:200]}",
        "safety_notes": "Backup mode — verify with field officer.",
        "citations": [c.get("metadata", {}).get("source", "") for c in chunks],
        "retrieved_chunks": chunks,
        "guardrail_triggered": False,
        "agent_trace": {"fallback": {"reason": error_note or "pipeline_error", "store": get_active_embedding_provider()}},
        "language": lang,
    }
