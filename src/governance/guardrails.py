"""Safety guardrails for recommendations."""
BLOCKED_PHRASES = [
    "guaranteed cure",
    "100% effective",
    "buy pesticide here",
    "definitely diseased",
    "no expert needed",
]

ESCALATION_REQUIRED_INTENTS = {"escalation", "insurance", "pest_disease"}


def check_output(text: str, intent: str) -> dict:
    lower = text.lower()
    triggered = []
    for phrase in BLOCKED_PHRASES:
        if phrase in lower:
            triggered.append(phrase)
    needs_expert = intent in ESCALATION_REQUIRED_INTENTS and "expert" not in lower and "field officer" not in lower
    if needs_expert:
        triggered.append("missing_expert_disclaimer")
    return {
        "passed": len(triggered) == 0,
        "triggers": triggered,
        "needs_safety_append": needs_expert or len(triggered) > 0,
    }


def apply_guardrails(text: str, intent: str) -> tuple[str, bool]:
    result = check_output(text, intent)
    if not result["needs_safety_append"]:
        return text, False
    suffix = (
        "\n\n---\n**Safety note:** This guidance is informational only. "
        "For pest outbreaks, disease confirmation, or insurance claims, "
        "please consult a GreenHarvest agriculture expert or field officer."
    )
    return text + suffix, True
