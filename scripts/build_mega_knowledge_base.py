"""Build 1000+ knowledge files: crops, pests, diseases, varieties, regions, FAQs."""
from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

KB = ROOT / "knowledge_base"
DATA = ROOT / "data"

from src.rag.crop_catalog import CROP_NAMES, normalize_crop

PESTS = (
    "aphids", "whitefly", "thrips", "bollworm", "stem_borer", "leaf_folder",
    "armyworm", "cutworm", "mites", "mealybug", "fruit_borer", "pod_borer",
    "hopper", "jassids", "nematodes", "termites", "root_grubs", "leaf_miner",
)

DISEASES = (
    "fungal_leaf_spot", "bacterial_blight", "rust", "powdery_mildew", "downy_mildew",
    "wilt", "root_rot", "virus_mosaic", "anthracnose", "blast", "smut", "dieback",
)

STATES = (
    "andhra_pradesh", "telangana", "karnataka", "tamil_nadu", "maharashtra",
    "gujarat", "rajasthan", "punjab", "haryana", "uttar_pradesh", "madhya_pradesh",
    "bihar", "west_bengal", "odisha", "kerala", "assam", "himachal_pradesh",
)

IRRIGATION_FAQ = (
    ("drip", "Drip saves water 30–50%; place lines near root zone; flush lines periodically."),
    ("sprinkler", "Sprinkler suits cereals and vegetables; avoid midday in heat."),
    ("rainfed", "Rainfed: conserve moisture with mulch, bunding, and early sowing after rains."),
    ("canal", "Canal irrigation: align with supply schedule; avoid waterlogging in clay soils."),
)


def _write(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body.strip() + "\n", encoding="utf-8")


def write_crop_guide(crop: str) -> None:
    c = normalize_crop(crop)
    body = f"""# {c.replace('_', ' ').title()} — cultivation guide

## Crop
{c}

## Sowing
- Use certified seed from licensed sources.
- Treat seed for soil-borne diseases where recommended.
- Sow at optimal window for your agro-climatic zone.

## Irrigation
- Match irrigation to growth stage — avoid prolonged waterlogging.
- Critical stages need consistent moisture; drain before harvest where applicable.

## Nutrition
- Basal DAP/phosphorus at sowing; nitrogen in splits per stage.
- Micronutrients (zinc, boron, iron) per soil test.

## Integrated pest management
- Scout weekly; economic threshold before spray.
- Prefer biocontrol and targeted chemistry.

## Harvest
- Harvest at physiological maturity for best price and quality.
- Dry grains to safe moisture before storage.

## GreenHarvest
Category: crops | Crop: {c}
"""
    _write(KB / "crops" / f"{c}.md", body)


def write_pest_note(crop: str, pest: str) -> None:
    c, p = normalize_crop(crop), pest.replace("_", " ")
    body = f"""# {c.title()} — {p} management

Crop: {c}
Pest: {pest}

## Identification
- Monitor lower/upper leaf surface and growing tips.
- Sticky honeydew, holes, mines, or wilting may indicate {p}.

## Cultural control
- Remove crop residues; avoid monoculture without rotation.
- Balanced nutrition — excess nitrogen increases sucking pests.

## Chemical / biological
- Use recommended molecule per state agriculture university.
- Rotate insecticide groups to delay resistance.
- Neem, BT, or biocontrol where effective for {p}.

Category: pests | Crop: {c}
"""
    _write(KB / "pests" / f"{c}_{pest}.md", body)


def write_disease_note(crop: str, disease: str) -> None:
    c, d = normalize_crop(crop), disease.replace("_", " ")
    body = f"""# {c.title()} — {d}

Crop: {c}
Disease: {disease}

## Symptoms
- Leaf spots, wilting, discoloration, or stunted growth may indicate {d}.
- Confirm with extension officer if unsure before fungicide/bactericide.

## Management
- Use resistant varieties when available.
- Improve drainage; avoid overhead irrigation late evening.
- Remove infected debris; treat seed for seed-borne issues.

Category: diseases | Crop: {c}
"""
    _write(KB / "diseases" / f"{c}_{disease}.md", body)


def write_variety_note(crop: str, variety: str, region: str) -> None:
    c = normalize_crop(crop)
    body = f"""# {crop.title()} variety: {variety}

- **Crop:** {c}
- **Variety:** {variety}
- **Suitable regions:** {region}
- Check local KVK for certified seed availability and duration.

Category: varieties | Crop: {c}
"""
    _write(KB / "varieties" / f"{c}_{variety.lower().replace(' ', '_')[:40]}.md", body)


def write_state_crop_note(state: str, crop: str) -> None:
    s, c = state.replace("_", " "), normalize_crop(crop)
    body = f"""# {c.title()} in {s.title()}

State: {state}
Crop: {c}

- Follow state agriculture department package of practices.
- Subsidy and insurance notifications vary by district.
- Contact district agriculture officer for variety recommendations.

Category: regional | State: {state} | Crop: {c}
"""
    _write(KB / "regional" / state / f"{c}.md", body)


def build_varieties_csv(count: int = 0) -> int:
    DATA.mkdir(parents=True, exist_ok=True)
    path = DATA / "crop_varieties.csv"
    rows = []
    suffixes = ["Hybrid", "Improved", "Local", "Bold", "Early", "Late", "Resistant", "Dwarf"]
    for crop in CROP_NAMES[:55]:
        c = normalize_crop(crop)
        for i, suf in enumerate(suffixes):
            rows.append({
                "crop": c,
                "variety_name": f"{c.title()} {suf} {(i+1)}",
                "duration_days": 90 + (i * 15) % 120,
                "region": "Pan-India (verify locally)",
            })
            write_variety_note(c, rows[-1]["variety_name"], rows[-1]["region"])
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["crop", "variety_name", "duration_days", "region"])
        w.writeheader()
        w.writerows(rows)
    return len(rows)


def build_crops_master_csv() -> int:
    path = DATA / "crops_master.csv"
    rows = []
    for crop in CROP_NAMES:
        c = normalize_crop(crop)
        rows.append({
            "crop": c,
            "category": "horticulture" if c in {"tomato", "mango", "grapes", "banana"} else "field",
            "season": "kharif" if c in {"cotton", "paddy", "maize", "soybean"} else "rabi",
            "water_need": "high" if c in {"paddy", "sugarcane", "banana"} else "medium",
        })
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    return len(rows)


def build_districts_csv() -> int:
    path = DATA / "districts_india.csv"
    districts = [
        ("Warangal", "Telangana", "semi_arid"), ("Guntur", "Andhra Pradesh", "tropical"),
        ("Nashik", "Maharashtra", "semi_arid"), ("Ludhiana", "Punjab", "temperate"),
        ("Hyderabad", "Telangana", "semi_arid"), ("Coimbatore", "Tamil Nadu", "tropical"),
        ("Indore", "Madhya Pradesh", "subtropical"), ("Patna", "Bihar", "humid"),
        ("Kolkata", "West Bengal", "humid"), ("Ahmedabad", "Gujarat", "arid"),
        ("Jaipur", "Rajasthan", "arid"), ("Bengaluru", "Karnataka", "tropical"),
        ("Lucknow", "Uttar Pradesh", "subtropical"), ("Bhopal", "Madhya Pradesh", "subtropical"),
        ("Raipur", "Chhattisgarh", "subtropical"), ("Guwahati", "Assam", "humid"),
    ]
    rows = [{"district": d, "state": s, "climate_zone": z} for d, s, z in districts]
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["district", "state", "climate_zone"])
        w.writeheader()
        w.writerows(rows)
    return len(rows)


def main():
    count = 0
    crops = [normalize_crop(c) for c in CROP_NAMES]
    print(f"Building KB for {len(crops)} crops...")

    for crop in crops:
        write_crop_guide(crop)
        count += 1
        for pest in PESTS:
            write_pest_note(crop, pest)
            count += 1
        for disease in DISEASES:
            write_disease_note(crop, disease)
            count += 1

    for state in STATES:
        for crop in crops[:25]:
            write_state_crop_note(state, crop)
            count += 1

    for topic, text in IRRIGATION_FAQ:
        _write(KB / "faqs" / f"irrigation_{topic}.md", f"# Irrigation — {topic}\n\n{text}\n")
        count += 1

    _write(
        KB / "faqs" / "other_crop_questions.md",
        """# Asking about a different crop than your profile

If your profile says cotton but you ask about tomato, GreenHarvest still answers using
tomato knowledge base content, with a clear note that tomato is not your registered profile crop.

Update **My farm** profile when you change your main crop for the season.
""",
    )
    count += 1

    v = build_varieties_csv()
    c = build_crops_master_csv()
    d = build_districts_csv()
    print(f"Wrote {count} markdown files under {KB}")
    print(f"CSV: crop_varieties={v}, crops_master={c}, districts={d}")
    print("Next: python scripts/ingest_kb.py")


if __name__ == "__main__":
    main()
