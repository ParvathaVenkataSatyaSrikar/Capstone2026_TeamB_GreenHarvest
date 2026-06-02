"""Main entry: run LangGraph pipeline and persist results."""
import time
from dataclasses import dataclass, field

from src.graph.workflow import get_support_graph
from src.db.repository import save_interaction, create_case
from src.governance.audit import log_pipeline_run
from src.analytics.trends import check_outbreak_patterns
from src.i18n.language import apply_farmer_language, normalize_language
from src.resilience.safe_pipeline import build_emergency_response
from config.settings import _load_env_file, get_settings


@dataclass
class SupportResult:
    farmer_id: str
    query: str
    intent: str = ""
    final_confidence: float = 0.0
    escalated: bool = False
    escalation_reason: str = ""
    review_status: str = "auto_approved"
    recommendation: str = ""
    translated_response: str = ""
    farmer_response: str = ""
    draft_response: str = ""
    staff_summary: str = ""
    safety_notes: str = ""
    citations: list = field(default_factory=list)
    agent_trace: dict = field(default_factory=dict)
    guardrail_triggered: bool = False
    interaction_id: int | None = None
    case_id: int | None = None
    response_time_ms: int = 0
    needs_human_review: bool = False
    language: str = "english"
    vision_provider: str = ""
    vision_confidence: float = 0.0


def run_image_diagnosis(
    farmer_id: str,
    image_bytes: bytes,
    mime: str = "image/jpeg",
    crop: str = "",
    district: str = "",
    farmer_note: str = "",
    language: str = "english",
    user_role: str = "farmer",
) -> SupportResult:
    """Analyze uploaded crop image (vision APIs → KB fallback)."""
    from src.integrations.profile import get_profile
    from src.vision.disease_detector import analyze_crop_image

    lang = normalize_language(language)
    profile = get_profile(farmer_id) or {}
    crop = crop or profile.get("crop", "")
    district = district or profile.get("district", "")
    start = time.time()

    analysis = analyze_crop_image(
        image_bytes, mime=mime, crop=crop, district=district, farmer_note=farmer_note
    )
    query = f"[Image diagnosis] {analysis.diagnosis.label} — {farmer_note or 'crop photo'}"
    text = apply_farmer_language(analysis.formatted_response, lang)

    elapsed_ms = int((time.time() - start) * 1000)
    final_state = {
        "intent": "pest_disease",
        "final_confidence": analysis.diagnosis.confidence,
        "escalated": analysis.diagnosis.confidence < 0.55
        or analysis.diagnosis.issue_type in {"unclear", "disease", "pest"},
        "escalation_reason": "image_diagnosis",
        "needs_human_review": analysis.diagnosis.confidence < 0.6,
        "review_status": "pending_human"
        if analysis.diagnosis.confidence < 0.6
        else "auto_approved",
        "recommendation": text,
        "farmer_response": text,
        "draft_response": text,
        "citations": analysis.kb_snippets,
        "agent_trace": {
            "vision": {
                "provider": analysis.provider,
                "issue_type": analysis.diagnosis.issue_type,
                "confidence": analysis.diagnosis.confidence,
            }
        },
        "guardrail_triggered": False,
    }
    result = _result_from_state(
        final_state, farmer_id, query, lang, user_role, elapsed_ms, saved=True
    )
    result.vision_provider = analysis.provider
    result.vision_confidence = analysis.diagnosis.confidence
    return result


def run_support_query(
    farmer_id: str,
    query: str,
    user_role: str = "farmer",
    language: str = "english",
    staff_notes: str = "",
) -> SupportResult:
    lang = normalize_language(language)
    query = (query or "").strip()
    if not query:
        empty = build_emergency_response(farmer_id, "general farming question", lang, "empty query")
        return _result_from_state(empty, farmer_id, query, lang, user_role, 0, saved=False)

    start = time.time()
    try:
        graph = get_support_graph()
        initial = {
            "farmer_id": farmer_id,
            "query": query,
            "user_role": user_role,
            "language": lang,
            "staff_notes": staff_notes,
            "agent_trace": {},
        }
        final_state = graph.invoke(initial)
    except Exception as exc:
        note = f"AI service used backup mode ({type(exc).__name__})"
        final_state = build_emergency_response(farmer_id, query, lang, note)
        if isinstance(final_state.get("agent_trace"), dict):
            final_state["agent_trace"].setdefault("fallback", {})["error"] = str(exc)[:200]
    elapsed_ms = int((time.time() - start) * 1000)

    return _result_from_state(
        final_state, farmer_id, query, lang, user_role, elapsed_ms, saved=True
    )


def _result_from_state(
    final_state: dict,
    farmer_id: str,
    query: str,
    lang: str,
    user_role: str,
    elapsed_ms: int,
    saved: bool = True,
) -> SupportResult:
    farmer_visible = apply_farmer_language(final_state.get("farmer_response", ""), lang)
    draft = final_state.get("draft_response", "")
    interaction_id = None
    case_id = None

    if saved:
        try:
            interaction_id = save_interaction({
                "farmer_id": farmer_id,
                "query_text": query,
                "response_text": farmer_visible,
                "intent": final_state.get("intent"),
                "language": lang,
                "confidence": final_state.get("final_confidence"),
                "escalated": final_state.get("escalated", False),
                "agent_trace": final_state.get("agent_trace", {}),
                "citations": final_state.get("citations", []),
                "response_time_ms": elapsed_ms,
                "review_status": final_state.get("review_status", "auto_approved"),
                "draft_response": draft or final_state.get("draft_response"),
            })
        except Exception:
            pass

        try:
            if final_state.get("escalated") or final_state.get("review_status") == "pending_human":
                if interaction_id:
                    case_id = create_case({
                        "interaction_id": interaction_id,
                        "farmer_id": farmer_id,
                        "priority": "high" if final_state.get("escalated") else "medium",
                        "summary": final_state.get("staff_summary", ""),
                        "assigned_role": "agriculture_expert",
                    })
        except Exception:
            pass

        try:
            check_outbreak_patterns()
            log_pipeline_run(
                interaction_id=interaction_id,
                user_role=user_role,
                confidence=final_state.get("final_confidence", 0),
                chunk_ids=final_state.get("citations", []),
                guardrail_triggered=final_state.get("guardrail_triggered", False),
                details={
                    "intent": final_state.get("intent"),
                    "review_status": final_state.get("review_status"),
                    "language": lang,
                    "graph": "langgraph" if "fallback" not in final_state.get("agent_trace", {}) else "fallback",
                },
            )
        except Exception:
            pass

    return SupportResult(
        farmer_id=farmer_id,
        query=query,
        intent=final_state.get("intent", ""),
        final_confidence=final_state.get("final_confidence", 0),
        escalated=final_state.get("escalated", False),
        escalation_reason=final_state.get("escalation_reason", ""),
        review_status=final_state.get("review_status", "auto_approved"),
        recommendation=final_state.get("recommendation", ""),
        translated_response=farmer_visible,
        farmer_response=final_state.get("farmer_response", ""),
        draft_response=draft or final_state.get("draft_response", ""),
        staff_summary=final_state.get("staff_summary", ""),
        citations=final_state.get("citations", []),
        agent_trace=final_state.get("agent_trace", {}),
        guardrail_triggered=final_state.get("guardrail_triggered", False),
        interaction_id=interaction_id,
        case_id=case_id,
        response_time_ms=elapsed_ms,
        needs_human_review=final_state.get("needs_human_review", False),
        language=lang,
    )
