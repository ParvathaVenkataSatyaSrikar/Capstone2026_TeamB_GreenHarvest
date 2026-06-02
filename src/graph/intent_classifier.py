"""Lightweight intent classification — no LangChain / LangGraph imports."""

INTENT_KEYWORDS = {
    "pest": "pest_disease", "disease": "pest_disease", "yellow": "pest_disease",
    "whitefly": "pest_disease", "bollworm": "pest_disease",
    "irrigation": "irrigation", "irrigat": "irrigation", "drip": "irrigation",
    "fertilizer": "input_recommendation", "urea": "input_recommendation",
    "price": "market_price", "mandi": "market_price",
    "weather": "weather_advisory", "climate": "weather_advisory", "temperature": "weather_advisory",
    "rainfall": "weather_advisory", "forecast": "weather_advisory", "frost": "weather_advisory",
    "humidity": "weather_advisory", "heatwave": "weather_advisory",
    "insurance": "insurance", "scheme": "scheme_information", "pm-kisan": "scheme_information",
    "subsidy": "scheme_information",
    "soil": "soil_health", "ph": "soil_health",
}


def classify_intent_keywords(query: str) -> tuple[str, float, str] | None:
    """Return (intent, confidence, source) when a keyword matches, else None."""
    lower = query.lower()
    for keyword, label in INTENT_KEYWORDS.items():
        if keyword in lower:
            return label, 0.82, "keywords"
    return None


def classify_intent(query: str, *, use_llm: bool = False) -> tuple[str, float, str]:
    """Same logic as node_classify_intent — keyword-first, optional LLM fallback."""
    matched = classify_intent_keywords(query)
    if matched:
        return matched

    if use_llm:
        from src.chains.agri_chains import invoke_intent
        from src.rag.prompts import INTENT_LABELS

        classified = invoke_intent(query)
        if classified and classified.intent in INTENT_LABELS:
            return classified.intent, float(classified.confidence), "structured_llm"

    return "crop_advisory", 0.7, "default"
