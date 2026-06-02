"""Merge weather, schemes, lifecycle, cost, sustainability into pipeline context."""
from __future__ import annotations

from src.advisory.weather_alerts import get_weather_alerts
from src.advisory.scheme_recommender import recommend_schemes, format_schemes_for_prompt
from src.advisory.crop_lifecycle import get_lifecycle_context, format_lifecycle_for_prompt
from src.advisory.farm_insights import (
    cost_optimization_tips,
    sustainable_farming_tips,
    estimate_carbon_footprint,
    format_insights_for_prompt,
)


def build_advisory_context(profile: dict, entities: dict, intent: str, query: str) -> dict:
    crop = entities.get("crop") or profile.get("crop", "")
    district = entities.get("district") or profile.get("district", "")
    stage = entities.get("crop_stage") or profile.get("crop_stage", "")
    acres = float(profile.get("land_acres") or 0)
    irrigation = profile.get("irrigation_type", "")

    weather_alerts = get_weather_alerts(district, crop)
    schemes = recommend_schemes({**profile, "crop": crop, "district": district})
    lifecycle = get_lifecycle_context(crop, stage)
    cost = cost_optimization_tips(crop, query)
    sustainable = sustainable_farming_tips(crop, irrigation)
    carbon = estimate_carbon_footprint(crop, acres, irrigation)

    return {
        "weather_alerts": weather_alerts,
        "scheme_recommendations": schemes,
        "crop_lifecycle": lifecycle,
        "cost_tips": cost,
        "sustainable_tips": sustainable,
        "carbon_estimate": carbon,
        "advisory_text": _format_advisory_block(
            weather_alerts, schemes, lifecycle, cost, sustainable, carbon, intent
        ),
    }


def _format_advisory_block(
    weather_alerts, schemes, lifecycle, cost, sustainable, carbon, intent
) -> str:
    parts = [
        f"WEATHER ALERT: {weather_alerts['title']} — {weather_alerts['farmer_message']}",
        format_lifecycle_for_prompt(lifecycle),
        "ELIGIBLE SCHEMES:\n" + format_schemes_for_prompt(schemes),
    ]
    if intent in {"scheme_information", "input_recommendation", "crop_advisory", "insurance"}:
        parts.append(format_insights_for_prompt(cost, sustainable, carbon))
    return "\n\n".join(parts)
