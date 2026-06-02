"""Pydantic schemas for structured LLM output."""
from typing import List, Union

from pydantic import BaseModel, Field

from src.rag.prompts import INTENT_LABELS


class IntentClassification(BaseModel):
    """Intent classifier agent output."""

    intent: str = Field(description=f"One of: {', '.join(INTENT_LABELS)}")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence 0-1")


class IntakeEntities(BaseModel):
    """Entity extraction from farmer query."""

    crop: str = Field(default="", description="Crop name if mentioned")
    district: str = Field(default="", description="District if mentioned")
    issue_type: str = Field(default="", description="pest, irrigation, market, etc.")
    crop_stage: str = Field(default="", description="Growth stage if mentioned")
    season: str = Field(default="", description="kharif or rabi if inferable")


class FarmerRecommendation(BaseModel):
    """Grounded recommendation for the farmer."""

    recommendation: Union[str, List[str]] = Field(
        description="Farmer-friendly steps as string or list of steps"
    )
    safety_notes: str = Field(
        default="Follow local extension guidelines.",
        description="Safety notes for chemicals and pests",
    )
    confidence: float = Field(default=0.75, ge=0.0, le=1.0)


class StaffSummary(BaseModel):
    """Brief case summary for field officers."""

    bullets: List[str] = Field(
        description="3-5 bullet points summarizing the case for staff review"
    )
