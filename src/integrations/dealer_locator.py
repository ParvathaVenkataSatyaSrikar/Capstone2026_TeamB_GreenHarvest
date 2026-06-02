"""Licensed input dealer locator + quote requests — informational demo, not e-commerce."""
from __future__ import annotations

from typing import Any

# Static demo directory — replace with real agri-dealer API in production.
MOCK_DEALERS: list[dict[str, Any]] = [
    {
        "name": "Sri Lakshmi Agro Inputs",
        "district": "Warangal",
        "village": "Hanamkonda",
        "licensed": True,
        "inputs": ["pesticide", "fertilizer", "seed"],
        "phone": "9876501001",
        "distance_km": 8,
    },
    {
        "name": "Green Valley Fertilizers",
        "district": "Warangal",
        "village": "Kazipet",
        "licensed": True,
        "inputs": ["fertilizer", "micronutrients"],
        "phone": "9876501002",
        "distance_km": 14,
    },
    {
        "name": "Krishna Seeds & Crop Care",
        "district": "Nizamabad",
        "village": "Armoor",
        "licensed": True,
        "inputs": ["seed", "pesticide"],
        "phone": "9876501003",
        "distance_km": 22,
    },
    {
        "name": "Punjab Agro Supply (Demo)",
        "district": "Ludhiana",
        "village": "Model Town",
        "licensed": True,
        "inputs": ["fertilizer", "pesticide", "seed"],
        "phone": "9876501004",
        "distance_km": 5,
    },
]

INPUT_TYPES = ["pesticide", "fertilizer", "seed", "micronutrients", "other"]


def find_dealers(district: str, input_type: str = "pesticide", limit: int = 5) -> list[dict[str, Any]]:
    d = (district or "").strip().lower()
    it = (input_type or "pesticide").strip().lower()
    matches = []
    for dealer in MOCK_DEALERS:
        if it not in dealer.get("inputs", []) and it != "other":
            continue
        if d and d not in dealer["district"].lower():
            continue
        matches.append(dealer)
    if not matches and d:
        for dealer in MOCK_DEALERS:
            if it in dealer.get("inputs", []) or it == "other":
                matches.append({**dealer, "note": "Nearest demo dealer (different district)"})
    if not matches:
        matches = MOCK_DEALERS[:limit]
    return matches[:limit]
