"""Crop lifecycle tracking — stage-aware recommendations."""
from __future__ import annotations

import csv
from pathlib import Path

_DATA = Path(__file__).resolve().parents[2] / "data"
_CALENDAR_CACHE: list[dict] | None = None

LIFECYCLE_STAGES = (
    "sowing",
    "germination",
    "vegetative",
    "flowering",
    "harvesting",
)

# Map profile / legacy stage names to standard stage
_STAGE_ALIASES = {
    "tillering": "vegetative",
    "vegetative": "vegetative",
    "flowering": "flowering",
    "boll_formation": "flowering",
    "pod_fill": "flowering",
    "grain_fill": "harvesting",
    "harvest": "harvesting",
    "harvesting": "harvesting",
    "germination": "germination",
    "sowing": "sowing",
    "nursery": "germination",
}

_STAGE_ADVICE: dict[str, dict[str, str]] = {
    "cotton": {
        "sowing": "Use certified seed; treat with fungicide. Ensure soil moisture for emergence.",
        "germination": "Monitor for thrips; avoid waterlogging. Thin to optimal plant stand.",
        "vegetative": "Balance nitrogen; scout for sucking pests. Install pheromone traps where advised.",
        "flowering": "Critical irrigation; monitor pink bollworm. Avoid excess nitrogen.",
        "harvesting": "Harvest at proper boll opening; avoid rain on open bolls. Pick in dry weather.",
    },
    "paddy": {
        "sowing": "Treat seed; maintain nursery hygiene. Select variety matching season length.",
        "germination": "Maintain shallow water in nursery; protect from birds if needed.",
        "vegetative": "Top-dress nitrogen at tillering; manage weeds early.",
        "flowering": "Maintain water at panicle initiation; watch for blast in humid weather.",
        "harvesting": "Drain field 7–10 days before harvest; harvest at 20–24% grain moisture.",
    },
    "wheat": {
        "sowing": "Timely sowing; treat seed for smut. Ensure good seed-soil contact.",
        "germination": "Light irrigation if dry; watch for termites in rainfed areas.",
        "vegetative": "First nitrogen split; control broadleaf weeds early.",
        "flowering": "Avoid moisture stress; scout for yellow rust.",
        "harvesting": "Harvest at maturity; dry grains to safe moisture before storage.",
    },
    "tomato": {
        "sowing": "Use disease-free seedlings; harden before transplant.",
        "germination": "Avoid damping-off; ventilate nursery.",
        "vegetative": "Stake/prune as per variety; drip irrigation preferred.",
        "flowering": "Calcium spray if blossom end rot risk; monitor fruit borer.",
        "harvesting": "Pick at breaker stage for distant market; avoid bruising.",
    },
}


def normalize_stage(stage: str) -> str:
    s = (stage or "").lower().strip().replace(" ", "_")
    return _STAGE_ALIASES.get(s, s if s in LIFECYCLE_STAGES else "vegetative")


def _load_calendar() -> list[dict]:
    global _CALENDAR_CACHE
    if _CALENDAR_CACHE is not None:
        return _CALENDAR_CACHE
    path = _DATA / "crop_calendar.csv"
    if not path.exists():
        _CALENDAR_CACHE = []
        return _CALENDAR_CACHE
    with path.open(encoding="utf-8") as f:
        _CALENDAR_CACHE = list(csv.DictReader(f))
    return _CALENDAR_CACHE


def _tip_from_csv(crop: str, stage: str) -> str | None:
    stage_n = normalize_stage(stage)
    for row in _load_calendar():
        if row.get("crop", "").lower() == crop and row.get("stage", "").lower() == stage_n:
            return row.get("key_task") or row.get("water_need")
    return None


def get_lifecycle_context(crop: str, stage: str) -> dict:
    crop_l = (crop or "cotton").lower()
    stage_n = normalize_stage(stage)
    crop_advice = _STAGE_ADVICE.get(crop_l, _STAGE_ADVICE.get("cotton", {}))
    tip = _tip_from_csv(crop_l, stage_n) or crop_advice.get(
        stage_n, "Follow local package of practices for this growth stage."
    )
    return {
        "stage": stage_n,
        "stage_label": stage_n.replace("_", " ").title(),
        "crop": crop_l,
        "advice": tip,
        "all_stages": list(LIFECYCLE_STAGES),
    }


def format_lifecycle_for_prompt(ctx: dict) -> str:
    return (
        f"Growth stage: {ctx['stage_label']} ({ctx['stage']}). "
        f"Stage-specific guidance: {ctx['advice']}"
    )
