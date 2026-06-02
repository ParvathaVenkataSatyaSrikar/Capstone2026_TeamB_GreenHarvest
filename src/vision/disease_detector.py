"""Crop image analysis — OpenAI Vision → Gemini Vision → KB keyword fallback."""
from __future__ import annotations

import base64
import re
from dataclasses import dataclass
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from config.settings import get_settings
from src.rag.retriever import retrieve
from src.resilience.llm_router import (
    _build_gemini,
    _build_openai,
    _extract_content,
    _invoke_with_timeout,
    _set_provider,
)
from src.resilience.network import is_online
from src.vision.schemas import CropImageDiagnosis

VISION_SYSTEM = """You are an agriculture expert for Indian farmers.
Analyze the crop/plant image. Identify disease, pest attack, nutrient deficiency, or healthy crop.
Be practical and cautious — if unsure, say unclear and recommend expert visit.
Return structured JSON only."""


@dataclass
class ImageAnalysisResult:
    diagnosis: CropImageDiagnosis
    provider: str
    offline: bool
    kb_snippets: list[str]
    formatted_response: str


def _image_message_parts(image_bytes: bytes, mime: str, crop: str, district: str, note: str) -> list[dict]:
    b64 = base64.standard_b64encode(image_bytes).decode("ascii")
    text = (
        f"Crop (if known): {crop or 'unknown'}. District: {district or 'unknown'}.\n"
        f"Farmer note: {note or 'none'}.\n"
        "Diagnose visible symptoms. Issue type must be one of: "
        "disease, pest, nutrient_deficiency, healthy, unclear."
    )
    return [
        {"type": "text", "text": text},
        {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}},
    ]


def _parse_diagnosis(raw: str, crop: str) -> CropImageDiagnosis | None:
    try:
        from src.chains.schemas import FarmerRecommendation  # noqa: F401 — ensure pydantic loaded
        import json
        m = re.search(r"\{[\s\S]*\}", raw)
        if m:
            data = json.loads(m.group())
            return CropImageDiagnosis(**data)
    except Exception:
        pass
    return None


def _vision_openai(parts: list[dict]) -> CropImageDiagnosis | None:
    settings = get_settings()
    for model in (settings.openai_vision_model, "gpt-4o-mini"):
        llm = _build_openai(model)
        if not llm:
            return None
        try:
            structured = llm.with_structured_output(CropImageDiagnosis)
            return structured.invoke([
                SystemMessage(content=VISION_SYSTEM),
                HumanMessage(content=parts),
            ])
        except Exception:
            try:
                resp = _invoke_with_timeout(llm, [
                    SystemMessage(content=VISION_SYSTEM + " Reply as JSON."),
                    HumanMessage(content=parts),
                ])
                return _parse_diagnosis(_extract_content(resp), "")
            except Exception:
                continue
    return None


def _vision_gemini(parts: list[dict]) -> CropImageDiagnosis | None:
    settings = get_settings()
    for model in (settings.gemini_vision_model, settings.gemini_model, "gemini-2.5-flash-lite"):
        llm = _build_gemini(model)
        if not llm:
            return None
        try:
            structured = llm.with_structured_output(CropImageDiagnosis)
            return structured.invoke([
                SystemMessage(content=VISION_SYSTEM),
                HumanMessage(content=parts),
            ])
        except Exception:
            continue
    return None


def _kb_fallback(crop: str, note: str) -> CropImageDiagnosis:
    query = f"{crop} leaf disease pest yellow spots fungal {note}".strip()
    chunks = retrieve(query, crop=crop, top_k=4)
    actions: list[str] = []
    label = "Possible crop stress — expert review recommended"
    issue = "unclear"
    conf = 0.42

    if chunks:
        text = " ".join(c["text"][:200] for c in chunks[:2]).lower()
        if any(w in text for w in ("pest", "bollworm", "aphid", "thrips")):
            issue, label, conf = "pest", "Possible pest damage (from crop guides)", 0.55
        elif any(w in text for w in ("fungal", "blight", "rust", "mildew", "spot")):
            issue, label, conf = "disease", "Possible fungal/bacterial issue (from crop guides)", 0.58
        elif any(w in text for w in ("nitrogen", "yellowing", "deficiency", "chlorosis")):
            issue, label, conf = "nutrient_deficiency", "Possible nutrient deficiency", 0.52
        for i, ch in enumerate(chunks[:3], 1):
            snippet = ch["text"].strip().split(".")[0][:120]
            if snippet:
                actions.append(f"{i}. {snippet}.")

    if not actions:
        actions = [
            "1. Share clearer photos (leaf top and bottom) with your field officer.",
            "2. Note crop stage and recent sprays.",
            "3. Visit nearest Krishi Vigyan Kendra for lab confirmation.",
        ]

    return CropImageDiagnosis(
        issue_type=issue,
        label=label,
        confidence=conf,
        recommended_actions=actions,
        safety_notes="Offline KB mode — vision APIs unavailable. Expert confirmation advised.",
    )


def _format_response(d: CropImageDiagnosis, provider: str, offline: bool) -> str:
    lines = [
        f"**Diagnosis:** {d.label}",
        f"**Type:** {d.issue_type.replace('_', ' ').title()}",
        f"**Confidence:** {int(d.confidence * 100)}%",
        "",
        "**Recommended actions:**",
    ]
    for step in d.recommended_actions:
        lines.append(f"- {step}")
    lines.extend(["", f"**Safety:** {d.safety_notes}", ""])
    if offline:
        lines.append("*(Answer from local crop guides — connect API keys for AI vision.)*")
    else:
        lines.append(f"*(Analyzed with {provider.replace('_', ' ')})*")
    return "\n".join(lines)


def analyze_crop_image(
    image_bytes: bytes,
    mime: str = "image/jpeg",
    crop: str = "",
    district: str = "",
    farmer_note: str = "",
) -> ImageAnalysisResult:
    if not image_bytes:
        d = CropImageDiagnosis(
            issue_type="unclear",
            label="No image provided",
            confidence=0.0,
            recommended_actions=["Upload a clear photo of the affected leaf or plant part."],
        )
        return ImageAnalysisResult(d, "none", True, [], _format_response(d, "none", True))

    parts = _image_message_parts(image_bytes, mime, crop, district, farmer_note)
    provider = "offline_rag"
    offline = True
    diagnosis: CropImageDiagnosis | None = None

    if is_online():
        diagnosis = _vision_openai(parts)
        if diagnosis:
            provider, offline = "openai_vision", False
            _set_provider("openai")
        if diagnosis is None:
            diagnosis = _vision_gemini(parts)
            if diagnosis:
                provider, offline = "gemini_vision", False
                _set_provider("gemini")

    if diagnosis is None:
        diagnosis = _kb_fallback(crop, farmer_note)

    query = f"{crop} {diagnosis.label} {diagnosis.issue_type}"
    chunks = retrieve(query, crop=crop, top_k=3)
    kb = [c.get("metadata", {}).get("source", "") for c in chunks]

    return ImageAnalysisResult(
        diagnosis=diagnosis,
        provider=provider,
        offline=offline,
        kb_snippets=kb,
        formatted_response=_format_response(diagnosis, provider, offline),
    )
