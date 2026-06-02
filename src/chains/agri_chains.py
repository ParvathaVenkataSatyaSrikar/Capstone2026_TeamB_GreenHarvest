"""LangChain LCEL chains — prompt | llm | parser."""
from __future__ import annotations

from functools import lru_cache
from typing import Any

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from src.chains.llm_factory import get_chat_model, get_primary_chat_model
from src.chains.schemas import FarmerRecommendation, IntakeEntities, IntentClassification, StaffSummary
from src.rag.prompts import INTENT_LABELS, SYSTEM_AGRI


def _format_recommendation(rec: FarmerRecommendation) -> tuple[str, str, float]:
    recommendation = rec.recommendation
    if isinstance(recommendation, list):
        text = "\n".join(f"- {item}" for item in recommendation)
    else:
        text = str(recommendation)
    return text, rec.safety_notes, float(rec.confidence)


@lru_cache(maxsize=1)
def build_guide_chain():
    """Guide assistant chain: prompt | llm | StrOutputParser."""
    prompt = ChatPromptTemplate.from_messages([
        ("system", "{system}"),
        ("human", "{question}"),
    ])
    return prompt | get_chat_model() | StrOutputParser()


@lru_cache(maxsize=1)
def build_intent_chain():
    llm = get_primary_chat_model()
    if llm is None:
        return None
    labels = ", ".join(INTENT_LABELS)
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            f"Classify the farmer query into exactly one intent: {labels}. "
            "Return structured JSON only.",
        ),
        ("human", "{query}"),
    ])
    return prompt | llm.with_structured_output(IntentClassification)


@lru_cache(maxsize=1)
def build_intake_chain():
    llm = get_primary_chat_model()
    if llm is None:
        return None
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "Extract crop, district, issue_type, crop_stage, season from the farmer query. "
            "Use profile hints when the query omits them.",
        ),
        ("human", "Query: {query}\nProfile crop: {crop}\nProfile district: {district}"),
    ])
    return prompt | llm.with_structured_output(IntakeEntities)


@lru_cache(maxsize=1)
def build_recommendation_chain():
    llm = get_primary_chat_model()
    if llm is None:
        return None
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_AGRI),
        (
            "human",
            """{lang_block}

Query: {query}
Intent: {intent}
Context: {context}
Knowledge: {kb}

Use context (weather alerts, growth stage, schemes, sustainability) plus knowledge base.
If context notes the farmer asked about a different crop than their profile, keep that note at the top.
Mention relevant scheme or weather alert when applicable. Ground advice in knowledge section.""",
        ),
    ])
    return prompt | llm.with_structured_output(FarmerRecommendation)


@lru_cache(maxsize=1)
def build_staff_summary_chain():
    llm = get_primary_chat_model()
    if llm is None:
        return None
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You summarize farmer support cases for agriculture field officers. "
            "Return 3-5 concise bullet points.",
        ),
        (
            "human",
            """Query: {query}
Intent: {intent}
Crop/District: {entities}
Escalated: {escalated} ({escalation_reason})
Recommendation excerpt: {recommendation}
Confidence: {confidence}""",
        ),
    ])
    return prompt | llm.with_structured_output(StaffSummary)


def invoke_intent(query: str) -> IntentClassification | None:
    chain = build_intent_chain()
    if chain is None:
        return None
    try:
        return chain.invoke({"query": query})
    except Exception:
        return None


def invoke_intake(query: str, crop: str, district: str) -> IntakeEntities | None:
    chain = build_intake_chain()
    if chain is None:
        return None
    try:
        return chain.invoke({"query": query, "crop": crop, "district": district})
    except Exception:
        return None


def invoke_recommendation(
    lang_block: str,
    query: str,
    intent: str,
    context: str,
    kb: str,
) -> FarmerRecommendation | None:
    chain = build_recommendation_chain()
    if chain is None:
        return None
    try:
        return chain.invoke({
            "lang_block": lang_block,
            "query": query,
            "intent": intent,
            "context": context,
            "kb": kb,
        })
    except Exception:
        return None


def invoke_staff_summary(payload: dict[str, Any]) -> str | None:
    chain = build_staff_summary_chain()
    if chain is None:
        return None
    try:
        result: StaffSummary = chain.invoke(payload)
        return "\n".join(f"- {b}" for b in result.bullets)
    except Exception:
        return None


def format_farmer_recommendation(rec: FarmerRecommendation) -> tuple[str, str, float]:
    return _format_recommendation(rec)
