"""Confidence scoring utilities."""
def combine_confidence(intent_conf: float, retrieval_conf: float, model_conf: float) -> float:
    weights = (0.25, 0.35, 0.40)
    score = intent_conf * weights[0] + retrieval_conf * weights[1] + model_conf * weights[2]
    return round(min(max(score, 0.0), 1.0), 2)


def confidence_label(score: float) -> str:
    if score >= 0.75:
        return "high"
    if score >= 0.55:
        return "medium"
    return "low"


def confidence_color(score: float) -> str:
    if score >= 0.75:
        return "#2e7d32"
    if score >= 0.55:
        return "#f9a825"
    return "#c62828"
