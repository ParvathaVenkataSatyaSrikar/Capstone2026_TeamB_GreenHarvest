"""Structured output for crop image analysis."""
from pydantic import BaseModel, Field


class CropImageDiagnosis(BaseModel):
    issue_type: str = Field(
        description="One of: disease, pest, nutrient_deficiency, healthy, unclear"
    )
    label: str = Field(description="Short diagnosis label, e.g. fungal leaf spot")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence 0-1")
    recommended_actions: list[str] = Field(
        description="2-5 practical farmer steps"
    )
    safety_notes: str = Field(
        default="Confirm with local KVK before spraying chemicals.",
        description="Safety and escalation notes",
    )
