"""LangGraph node functions — LangChain LCEL and Pydantic structured output."""
import json

from langchain_core.prompts import ChatPromptTemplate

from config.settings import get_settings
from src.chains.agri_chains import (
    format_farmer_recommendation,
    invoke_intake,
    invoke_intent,
    invoke_recommendation,
    invoke_staff_summary,
)
from src.chains.llm_factory import get_chat_model
from src.chains.rag_chain import format_chunks_for_prompt, search_knowledge_base
from src.db.repository import get_recent_interactions
from src.governance.confidence import combine_confidence
from src.governance.guardrails import apply_guardrails
from src.i18n.language import language_directive, normalize_language, pending_message
from src.integrations.market import compare_nearby_mandis, format_market_answer, get_market_price
from src.integrations.profile import get_profile
from src.integrations.query_focus import CSV_INTEGRATION_INTENTS, integration_focus
from src.integrations.soil import format_soil_answer, get_soil_report
from src.integrations.insurance_guide import format_insurance_answer
from src.integrations.weather import format_weather_answer
from src.integrations.tavily_search import format_for_context, run_tavily_search, tavily_available
from src.advisory.context_builder import build_advisory_context
from src.integrations.weather import get_weather
from src.rag.crop_catalog import CROP_NAMES, detect_crop_in_text, normalize_crop
from src.rag.crop_mismatch import build_crop_mismatch_notice, get_effective_query_crop
from src.graph.intent_classifier import INTENT_KEYWORDS, classify_intent_keywords
from src.rag.prompts import INTENT_LABELS, SYSTEM_AGRI


def _trace(state: dict, step: str, data: dict) -> dict:
    trace = dict(state.get("agent_trace", {}))
    trace[step] = data
    return {"agent_trace": trace}


def node_intake(state: dict) -> dict:
    profile = get_profile(state["farmer_id"]) or {}
    query = state["query"]
    if state.get("staff_notes"):
        query = f"{query}\n[Staff notes: {state['staff_notes']}]"

    lower = query.lower()
    crop = profile.get("crop", "")
    detected = detect_crop_in_text(query)
    if detected:
        crop = detected
    else:
        for name in CROP_NAMES:
            if name in lower:
                crop = normalize_crop(name)
                break

    district = profile.get("district", "")
    issue_type = ""
    for kw, label in [
        ("pest", "pest"), ("disease", "disease"), ("irrigation", "irrigation"),
        ("fertilizer", "input"), ("price", "market"), ("insurance", "insurance"),
    ]:
        if kw in lower:
            issue_type = label
            break

    entities = {
        "crop": crop,
        "district": district,
        "crop_stage": profile.get("crop_stage", ""),
        "issue_type": issue_type,
    }

    settings = get_settings()
    need_llm_intake = not (
        settings.skip_llm_intake_when_keywords
        and crop
        and district
        and issue_type
    )
    extracted = invoke_intake(query, crop, district) if need_llm_intake else None
    if extracted:
        if extracted.crop:
            entities["crop"] = extracted.crop
        if extracted.district:
            entities["district"] = extracted.district
        if extracted.issue_type:
            entities["issue_type"] = extracted.issue_type
        if extracted.crop_stage:
            entities["crop_stage"] = extracted.crop_stage
        if extracted.season:
            entities["season"] = extracted.season

    profile_crop = normalize_crop(profile.get("crop", ""))
    query_crop, mismatch_crop = get_effective_query_crop(profile_crop, query, entities)
    if query_crop:
        entities["crop"] = query_crop
    notice = ""
    if mismatch_crop:
        notice = build_crop_mismatch_notice(profile_crop, mismatch_crop, state.get("language", "english"))

    return {
        "farmer_profile": profile,
        "entities": entities,
        "profile_crop": profile_crop,
        "query_crop": query_crop or profile_crop,
        "crop_mismatch": bool(mismatch_crop),
        "crop_mismatch_notice": notice,
        **_trace(state, "intake", {
            **entities,
            "profile_crop": profile_crop,
            "query_crop": query_crop,
            "mismatch": bool(mismatch_crop),
            "source": "structured_llm" if extracted else "keywords",
        }),
    }


def node_classify_intent(state: dict) -> dict:
    intent = "crop_advisory"
    confidence = 0.7

    matched = classify_intent_keywords(state["query"])
    if matched:
        label, conf, source = matched
        return {
            "intent": label,
            "intent_confidence": conf,
            **_trace(state, "intent_classifier", {
                "intent": label, "confidence": conf, "source": source,
            }),
        }

    classified = invoke_intent(state["query"])
    if classified and classified.intent in INTENT_LABELS:
        return {
            "intent": classified.intent,
            "intent_confidence": float(classified.confidence),
            **_trace(state, "intent_classifier", {
                "intent": classified.intent,
                "confidence": classified.confidence,
                "source": "structured_llm",
            }),
        }

    return {
        "intent": intent,
        "intent_confidence": confidence,
        **_trace(state, "intent_classifier", {"intent": intent, "confidence": confidence, "source": "default"}),
    }


def node_retrieve_knowledge(state: dict) -> dict:
    intent = state.get("intent", "")
    focus = integration_focus(state.get("query", ""))
    if intent in CSV_INTEGRATION_INTENTS or focus:
        cites = []
        if intent == "market_price" or "market" in focus:
            cites.append("data/market_prices.csv")
        if intent == "weather_advisory" or "weather" in focus:
            cites.append("data/weather.csv")
        if intent == "soil_health" or "soil" in focus:
            cites.append("data/soil_reports.csv")
        if intent == "insurance" or "insurance" in focus:
            cites.append("data/scheme_eligibility.csv")
        return {
            "retrieved_chunks": [],
            "citations": cites or ["data/integrations"],
            "retrieval_confidence": 0.9,
            **_trace(state, "knowledge_retrieval", {
                "chunks": 0, "score": 0.9, "source": "integration_csv", "focus": list(focus),
            }),
        }
    crop = state.get("query_crop") or state.get("entities", {}).get("crop", "")
    chunks = search_knowledge_base(state["query"], crop=crop, top_k=5)
    citations = [c.get("metadata", {}).get("source", c.get("id", "")) for c in chunks]
    retrieval_confidence = max((c.get("score", 0) for c in chunks), default=0.0)
    return {
        "retrieved_chunks": chunks,
        "citations": citations,
        "retrieval_confidence": retrieval_confidence,
        **_trace(state, "knowledge_retrieval", {"chunks": len(chunks), "score": retrieval_confidence}),
    }


def node_build_context(state: dict) -> dict:
    profile = state.get("farmer_profile", {})
    district = state.get("entities", {}).get("district") or profile.get("district", "")
    crop = state.get("query_crop") or state.get("entities", {}).get("crop") or profile.get("crop", "")
    farmer_id = state["farmer_id"]

    entities = state.get("entities", {})
    advisory = build_advisory_context(
        profile, entities, state.get("intent", ""), state.get("query", "")
    )
    context = {
        "weather": get_weather(district, crop),
        "weather_alerts": advisory["weather_alerts"],
        "soil": get_soil_report(farmer_id, district, crop),
        "crop_lifecycle": advisory["crop_lifecycle"],
        "scheme_recommendations": advisory["scheme_recommendations"],
        "cost_tips": advisory["cost_tips"],
        "sustainable_tips": advisory["sustainable_tips"],
        "carbon_estimate": advisory["carbon_estimate"],
        "advisory_summary": advisory["advisory_text"],
        "recent_queries": [
            {"query": i.get("query_text"), "intent": i.get("intent")}
            for i in get_recent_interactions(farmer_id, 5)
        ],
    }
    if state.get("intent") == "market_price":
        context["market"] = get_market_price(district, crop)
        context["mandi_comparison"] = compare_nearby_mandis(crop)

    if state.get("intent") in {"market_price", "scheme_information", "insurance"} and tavily_available():
        web_q = f"{state['query']} {crop} {district} India agriculture"
        snippets = run_tavily_search(web_q, max_results=3)
        if snippets:
            context["web_research"] = snippets
            context["web_summary"] = format_for_context(snippets)

    return {
        "context": context,
        **_trace(state, "context_analysis", {
            "district": district,
            "crop": crop,
            "weather_alert": advisory["weather_alerts"].get("primary_alert"),
            "lifecycle_stage": advisory["crop_lifecycle"].get("stage"),
            "schemes": len(advisory["scheme_recommendations"]),
            "tavily": bool(context.get("web_research")),
        }),
    }


def _recommendation_from_chunks(chunks: list) -> tuple[str, str, float]:
    if not chunks:
        return (
            "Consult your nearest Krishi Vigyan Kendra or field officer for this question.",
            "Expert review recommended.",
            0.35,
        )
    steps: list[str] = []
    for i, ch in enumerate(chunks[:3], 1):
        body = ch["text"].strip()
        lines = [
            ln.strip().lstrip("-•").strip()
            for ln in body.splitlines()
            if ln.strip() and not ln.strip().startswith("#")
        ]
        snippet = " ".join(lines[:5])[:380]
        if snippet:
            steps.append(f"{i}. {snippet}")
    recommendation = "\n".join(steps) if steps else chunks[0]["text"][:500]
    source = chunks[0].get("metadata", {}).get("source", "GreenHarvest KB")
    safety = f"Based on {source}. Verify with your field officer before applying chemicals."
    return recommendation, safety, 0.58


def _integration_recommendation(state: dict) -> dict | None:
    """Deterministic CSV-backed answers (market, weather, soil)."""
    intent = state.get("intent", "")
    focus = integration_focus(state.get("query", ""))
    if intent == "weather_advisory":
        focus.add("weather")
    if intent == "soil_health":
        focus.add("soil")
    if intent == "market_price":
        focus.add("market")
    if intent == "insurance":
        focus = {"insurance"}
    if not focus:
        return None

    profile = state.get("farmer_profile", {})
    district = state.get("entities", {}).get("district") or profile.get("district", "")
    crop = state.get("query_crop") or state.get("entities", {}).get("crop") or profile.get("crop", "")
    farmer_id = state["farmer_id"]
    query = state.get("query", "")
    parts: list[str] = []
    if "insurance" in focus:
        parts.append(format_insurance_answer(farmer_id, district, crop, query=query))
    if "market" in focus:
        parts.append(format_market_answer(district, crop, language=normalize_language(state.get("language"))))
    if "weather" in focus:
        parts.append(format_weather_answer(district, crop))
    if "soil" in focus:
        parts.append(format_soil_answer(farmer_id, district, crop))

    recommendation = "\n\n".join(parts)
    mismatch_note = state.get("crop_mismatch_notice", "")
    if mismatch_note:
        recommendation = f"{mismatch_note}\n\n{recommendation}"

    safety_bits = []
    if "market" in focus:
        safety_bits.append("Confirm mandi rates at your local market before selling.")
    if "weather" in focus:
        safety_bits.append("Check official weather bulletins before spraying or harvesting.")
    if "soil" in focus:
        safety_bits.append("Confirm fertilizer doses with a soil test or extension officer.")
    if "insurance" in focus:
        safety_bits.append(
            "File claims only through official PMFBY/insurer channels; keep all receipts and photos."
        )

    return {
        "recommendation": recommendation,
        "safety_notes": " ".join(safety_bits) or "Follow local extension guidelines.",
        "model_confidence": 0.92,
        **_trace(state, "recommendation", {
            "grounded": True,
            "source": "integration_csv",
            "focus": list(focus),
            "crop": crop,
            "district": district,
        }),
    }


def node_generate_recommendation(state: dict) -> dict:
    integrated = _integration_recommendation(state)
    if integrated:
        return integrated

    settings = get_settings()
    chunks = state.get("retrieved_chunks", [])
    if not chunks and state.get("retrieval_confidence", 0) < settings.retrieval_min_score:
        return {
            "recommendation": "Insufficient trusted data. A GreenHarvest expert will review your query.",
            "safety_notes": "Expert review required.",
            "model_confidence": 0.3,
            **_trace(state, "recommendation", {"grounded": False}),
        }

    kb_text = format_chunks_for_prompt(chunks)
    ctx = state.get("context", {})
    advisory_block = ctx.get("advisory_summary", "")
    context_text = (advisory_block + "\n\n" + json.dumps(ctx, default=str))[:2200]
    lang = normalize_language(state.get("language"))
    lang_block = language_directive(lang)
    mismatch_note = state.get("crop_mismatch_notice", "")

    structured = invoke_recommendation(
        lang_block, state["query"], state.get("intent", ""), context_text, kb_text
    )
    if structured:
        recommendation, safety_notes, model_confidence = format_farmer_recommendation(structured)
        if mismatch_note:
            recommendation = f"{mismatch_note}\n\n{recommendation}"
        return {
            "recommendation": recommendation,
            "safety_notes": safety_notes,
            "model_confidence": model_confidence,
            **_trace(state, "recommendation", {"grounded": True, "source": "structured_llm", "crop_mismatch": bool(mismatch_note)}),
        }

    llm = get_chat_model()
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_AGRI),
        ("human", """{lang_block}

Query: {query}
Intent: {intent}
Context: {context}
Knowledge: {kb}"""),
    ])
    msg = (prompt | llm).invoke({
        "lang_block": lang_block,
        "query": state["query"],
        "intent": state.get("intent", ""),
        "context": context_text,
        "kb": kb_text,
    })
    text = msg.content if hasattr(msg, "content") else str(msg)
    meta = getattr(msg, "response_metadata", {}) or {}

    if meta.get("offline") and chunks:
        recommendation, safety_notes, model_confidence = _recommendation_from_chunks(chunks)
        if mismatch_note:
            recommendation = f"{mismatch_note}\n\n{recommendation}"
        return {
            "recommendation": recommendation,
            "safety_notes": safety_notes,
            "model_confidence": model_confidence,
            **_trace(state, "recommendation", {"grounded": True, "offline": True}),
        }

    recommendation, safety_notes, model_confidence = text, "Follow local extension guidelines.", 0.75
    if mismatch_note:
        recommendation = f"{mismatch_note}\n\n{recommendation}"
    return {
        "recommendation": recommendation,
        "safety_notes": safety_notes,
        "model_confidence": model_confidence,
        **_trace(state, "recommendation", {"grounded": True, "source": "lcel_fallback"}),
    }


def node_staff_summary(state: dict) -> dict:
    summary = None
    if state.get("escalated") or state.get("needs_human_review"):
        summary = invoke_staff_summary({
            "query": state["query"],
            "intent": state.get("intent", ""),
            "entities": str(state.get("entities", {})),
            "escalated": state.get("escalated", False),
            "escalation_reason": state.get("escalation_reason", ""),
            "recommendation": (state.get("recommendation") or "")[:500],
            "confidence": state.get("model_confidence", 0),
        })
    if not summary:
        summary = (
            f"Farmer {state['farmer_id']} ({state.get('entities', {}).get('crop', '')}, "
            f"{state.get('entities', {}).get('district', '')})\n"
            f"Intent: {state.get('intent')} · Confidence: {state.get('model_confidence', 0)}\n"
            f"Query: {state['query'][:200]}\n"
            f"Advice preview: {(state.get('recommendation') or '')[:400]}"
        )
    return {
        "staff_summary": summary,
        **_trace(state, "interaction_summary", {"source": "structured_llm" if summary.startswith("-") else "template"}),
    }


def node_escalation_check(state: dict) -> dict:
    settings = get_settings()
    final_confidence = combine_confidence(
        state.get("intent_confidence", 0),
        state.get("retrieval_confidence", 0),
        state.get("model_confidence", 0),
    )
    reasons = []
    intent = state.get("intent", "")
    retrieval = state.get("retrieval_confidence", 0)
    rec_trace = state.get("agent_trace", {}).get("recommendation", {})
    csv_grounded = (
        state.get("intent") in CSV_INTEGRATION_INTENTS
        or rec_trace.get("source") in ("integration_csv", "market_csv", "weather_csv", "soil_csv")
    )
    has_grounded_answer = csv_grounded or (
        bool(state.get("retrieved_chunks")) and retrieval >= settings.retrieval_min_score
    )

    if final_confidence < settings.escalation_confidence_threshold and not csv_grounded:
        reasons.append("low_confidence")
    if intent in {"insurance", "escalation"}:
        reasons.append(f"intent_{intent}")
    elif intent == "pest_disease" and (not has_grounded_answer or final_confidence < 0.62):
        reasons.append("intent_pest_disease")
    for word in ["outbreak", "emergency", "urgent", "severe"]:
        if word in state["query"].lower():
            reasons.append(f"keyword_{word}")
            break

    escalated = len(reasons) > 0 and not csv_grounded
    needs_human = escalated and (
        intent in {"insurance", "escalation"}
        or not has_grounded_answer
        or final_confidence < 0.58
        or any(r.startswith("keyword_") for r in reasons)
    )
    return {
        "final_confidence": final_confidence,
        "escalated": escalated,
        "escalation_reason": ", ".join(reasons),
        "needs_human_review": needs_human,
        **_trace(state, "escalation", {"escalated": escalated, "reasons": reasons, "needs_human": needs_human}),
    }


def node_human_review_gate(state: dict) -> dict:
    draft = state.get("recommendation", "")
    if state.get("safety_notes"):
        draft += f"\n\nSafety: {state['safety_notes']}"
    draft, guardrail_hit = apply_guardrails(draft, state.get("intent", ""))

    lang = normalize_language(state.get("language"))
    if state.get("needs_human_review"):
        farmer_text = pending_message(lang)
        if draft and "Insufficient trusted data" not in draft:
            farmer_text += (
                "\n\n---\n\n**Preliminary guidance (expert will confirm):**\n\n"
                + draft[:1200]
                + ("\n\n…" if len(draft) > 1200 else "")
            )
        return {
            "draft_response": draft,
            "review_status": "pending_human",
            "farmer_response": farmer_text,
            "guardrail_triggered": guardrail_hit,
            **_trace(state, "human_review", {"status": "pending_human"}),
        }

    return {
        "draft_response": draft,
        "review_status": "auto_approved",
        "farmer_response": draft,
        "guardrail_triggered": guardrail_hit,
        **_trace(state, "human_review", {"status": "auto_approved"}),
    }


def route_after_human_gate(state: dict) -> str:
    if state.get("review_status") == "pending_human":
        return "save_pending"
    return "save_approved"
