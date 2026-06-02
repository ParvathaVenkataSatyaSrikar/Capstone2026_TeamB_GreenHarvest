"""Cost optimization, sustainable farming, carbon footprint estimates."""
from __future__ import annotations

from src.rag.retriever import retrieve


def cost_optimization_tips(crop: str, query: str = "") -> list[str]:
    crop_l = (crop or "").lower()
    tips = []
    generic = {
        "cotton": [
            "Compare generic recommended molecules with branded ones — same AI may cost less via dealer scheme.",
            "Use integrated pest management before broad-spectrum sprays to cut chemical spend.",
            "Split fertilizer based on soil test instead of flat high doses.",
        ],
        "paddy": [
            "Adopt SRI or line sowing where suitable to save seed cost.",
            "Use leaf colour chart for nitrogen — avoids over-fertilization.",
            "Group inputs purchase with FPO/cooperative for bulk rates.",
        ],
        "tomato": [
            "Drip + mulching reduces water and weed control cost.",
            "Use trap crops / pheromone traps before heavy pesticide sprays.",
        ],
    }
    tips.extend(generic.get(crop_l, [
        "Use soil test based fertilizer — often cheaper than blanket high doses.",
        "Buy inputs during government subsidy windows via licensed POS.",
    ]))

    chunks = retrieve(f"{crop} organic low cost fertilizer alternative", crop=crop_l, top_k=2)
    for ch in chunks:
        snippet = ch["text"].strip()[:180]
        if snippet and snippet not in tips:
            tips.append(snippet)
    return tips[:5]


def sustainable_farming_tips(crop: str, irrigation_type: str = "") -> list[str]:
    irr = (irrigation_type or "").lower()
    tips = [
        "Rotate crops or include legumes to improve soil organic matter.",
        "Use drip or sprinkler to reduce water waste vs flood irrigation.",
        "Leave crop residue or compost to build soil carbon and reduce erosion.",
    ]
    if "drip" in irr:
        tips.append("You already use drip — schedule irrigation using soil moisture, not calendar only.")
    elif "rainfed" in irr:
        tips.append("Rainfed: use contour bunding and mulching to capture rainfall.")
    if crop in {"cotton", "paddy"}:
        tips.append("Scout pests weekly — early action cuts pesticide load and protects beneficial insects.")
    return tips[:6]


def estimate_carbon_footprint(
    crop: str,
    land_acres: float,
    irrigation_type: str = "",
    fertilizer_level: str = "medium",
) -> dict:
    """Simple demo estimator (kg CO2e per season) — not a certified LCA."""
    acres = max(0.1, float(land_acres or 1.0))
    base_per_acre = {
        "paddy": 800,
        "rice": 800,
        "wheat": 450,
        "cotton": 550,
        "tomato": 400,
        "maize": 500,
    }.get((crop or "").lower(), 480)

    irr_mult = 1.0
    if "flood" in irrigation_type.lower() or "canal" in irrigation_type.lower():
        irr_mult = 1.25
    elif "drip" in irrigation_type.lower():
        irr_mult = 0.85
    elif "rainfed" in irrigation_type.lower():
        irr_mult = 0.75

    fert_mult = {"low": 0.8, "medium": 1.0, "high": 1.35}.get(fertilizer_level, 1.0)
    kg_co2e = round(base_per_acre * acres * irr_mult * fert_mult)

    reduction_tips = [
        "Reduce nitrogen dose using soil test — lowers nitrous oxide emissions.",
        "Switch flood irrigation to drip where possible.",
        "Use organic manure to replace part of chemical fertilizer.",
    ]
    return {
        "kg_co2e_estimated": kg_co2e,
        "land_acres": acres,
        "crop": crop,
        "band": "moderate" if kg_co2e < 1500 else "higher",
        "reduction_tips": reduction_tips,
        "disclaimer": "Demo estimate for awareness — not a certified carbon audit.",
    }


def format_insights_for_prompt(
    cost: list[str],
    sustainable: list[str],
    carbon: dict,
) -> str:
    lines = ["## Cost optimization", *[f"- {t}" for t in cost[:3]]]
    lines.append("## Sustainable practices")
    lines.extend(f"- {t}" for t in sustainable[:3])
    lines.append(
        f"## Carbon footprint (demo)\n"
        f"Estimated ~{carbon['kg_co2e_estimated']} kg CO2e this season ({carbon['band']}). "
        f"{carbon['disclaimer']}"
    )
    return "\n".join(lines)
