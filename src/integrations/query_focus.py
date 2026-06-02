"""Detect when a farmer query should use simulated CSV integrations (not generic LLM)."""
from __future__ import annotations

CSV_INTEGRATION_INTENTS = frozenset({
    "market_price",
    "weather_advisory",
    "soil_health",
    "insurance",
})


def _is_insurance_query(lower: str) -> bool:
    return any(
        k in lower
        for k in (
            "insurance",
            "insure",
            "pmfby",
            "crop insurance",
            "claim",
            "file crop",
            "policy",
        )
    )


def integration_focus(query: str) -> set[str]:
    """Return subset of: market, weather, soil, insurance."""
    lower = (query or "").lower()

    # Insurance/scheme claims must win over incidental words like "rainfall"
    if _is_insurance_query(lower):
        return {"insurance"}

    focus: set[str] = set()
    if any(k in lower for k in ("mandi", "price", "market rate", "selling price", "today's price")):
        focus.add("market")
    if any(
        k in lower
        for k in (
            "weather",
            "climate",
            "temperature",
            "rainfall",
            " rain ",
            "frost",
            "forecast",
            "humidity",
            "heatwave",
            "storm",
            "cold night",
        )
    ):
        focus.add("weather")
    if any(
        k in lower
        for k in ("soil", " ph", "npk", "nitrogen", "phosphorus", "potassium", "organic carbon")
    ):
        focus.add("soil")
    if "precaution" in lower and any(k in lower for k in ("weather", "cold", "frost", "rain", "temperature")):
        focus.add("weather")
    return focus
