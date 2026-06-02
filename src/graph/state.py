"""LangGraph state for the farmer support workflow."""
from typing import Annotated, TypedDict
import operator


class GraphState(TypedDict, total=False):
    farmer_id: str
    query: str
    user_role: str
    language: str
    staff_notes: str

    farmer_profile: dict
    entities: dict
    query_crop: str
    profile_crop: str
    crop_mismatch: bool
    crop_mismatch_notice: str
    intent: str
    intent_confidence: float

    retrieved_chunks: list
    citations: list
    retrieval_confidence: float
    context: dict

    recommendation: str
    safety_notes: str
    model_confidence: float
    final_confidence: float

    staff_summary: str
    escalated: bool
    escalation_reason: str
    needs_human_review: bool
    review_status: str

    draft_response: str
    farmer_response: str
    guardrail_triggered: bool

    agent_trace: Annotated[dict, operator.ior]
    interaction_id: int
    case_id: int
    response_time_ms: int
