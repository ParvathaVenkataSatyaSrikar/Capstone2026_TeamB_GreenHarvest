"""Expand CSV/notes datasets for advisory modules and demos."""
from __future__ import annotations

import csv
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
DATA = ROOT / "data"
NOTES = ROOT / "knowledge_base" / "notes"

from src.rag.crop_catalog import CROP_NAMES, normalize_crop

STAGES = ("sowing", "vegetative", "flowering", "fruiting", "harvest")
PESTS = ("aphids", "whitefly", "bollworm", "thrips", "leaf_spot", "rust", "blast")
SCHEMES = (
    ("pm_kisan", "PM-KISAN", "income_support", "all_crops"),
    ("pmfby", "PMFBY crop insurance", "insurance", "all_crops"),
    ("soil_health", "Soil Health Card", "soil_testing", "all_crops"),
    ("drip_subsidy", "Micro-irrigation subsidy", "irrigation", "horticulture"),
    ("seed_subsidy", "Certified seed subsidy", "inputs", "cereals"),
)


def write_crop_calendar() -> int:
    path = DATA / "crop_calendar.csv"
    rows = []
    for crop in CROP_NAMES:
        c = normalize_crop(crop)
        for stage in STAGES:
            rows.append({
                "crop": c,
                "stage": stage,
                "days_from_sowing_min": random.randint(0, 120),
                "days_from_sowing_max": random.randint(30, 180),
                "key_task": f"{stage} management for {c}",
                "water_need": random.choice(("low", "medium", "high")),
            })
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    return len(rows)


def write_pest_disease_lookup() -> int:
    path = DATA / "pest_disease_lookup.csv"
    rows = []
    for crop in CROP_NAMES[:40]:
        c = normalize_crop(crop)
        for pest in PESTS:
            rows.append({
                "crop": c,
                "issue_type": "pest" if pest in ("aphids", "whitefly", "bollworm", "thrips") else "disease",
                "issue_id": pest,
                "symptoms": f"Typical {pest} signs on {c}",
                "first_action": "Scout and confirm; use economic threshold before spray",
                "organic_option": "Neem oil / biocontrol where suitable",
            })
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    return len(rows)


def write_fertilizer_guide() -> int:
    path = DATA / "fertilizer_guide.csv"
    rows = []
    for crop in CROP_NAMES:
        c = normalize_crop(crop)
        rows.append({
            "crop": c,
            "basal_npk": "20:20:0 or DAP per soil test",
            "top_dress_n": "Split urea at tillering and panicle initiation",
            "micronutrients": "Zinc/boron if deficiency observed",
            "organic_alternative": "FYM 5–10 t/ha + green manure where possible",
        })
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    return len(rows)


def write_scheme_eligibility() -> int:
    path = DATA / "scheme_eligibility.csv"
    rows = []
    for sid, name, category, crops in SCHEMES:
        for crop in CROP_NAMES[:30]:
            rows.append({
                "scheme_id": sid,
                "scheme_name": name,
                "category": category,
                "crop": normalize_crop(crop),
                "eligible": "yes" if crops == "all_crops" or crop in {"tomato", "grapes", "banana"} else "check_state",
                "portal_hint": "state agriculture portal / UMANG",
            })
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    return len(rows)


def write_market_prices() -> int:
    path = DATA / "market_prices.csv"
    rows = []
    markets = ("Warangal", "Guntur", "Nashik", "Ludhiana", "Hyderabad")
    for crop in CROP_NAMES:
        c = normalize_crop(crop)
        for m in markets:
            base = random.randint(1200, 8500)
            rows.append({
                "date": "2026-05-20",
                "market": m,
                "crop": c,
                "min_price_inr_quintal": base - 200,
                "max_price_inr_quintal": base + 300,
                "modal_price_inr_quintal": base,
            })
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    return len(rows)


def write_field_notes() -> int:
    NOTES.mkdir(parents=True, exist_ok=True)
    topics = (
        ("intercropping", "Intercropping legumes with cereals improves nitrogen and risk spread."),
        ("mulching", "Organic mulch conserves moisture and suppresses weeds in rainfed plots."),
        ("soil_testing", "Test NPK and micronutrients every 2–3 years; apply only what is needed."),
        ("storage", "Dry grains to 12–14% moisture; use hermetic bags where available."),
        ("other_crop_advice", "When asking about a crop not on your profile, GreenHarvest answers with a clear profile notice."),
    )
    for name, body in topics:
        (NOTES / f"{name}.md").write_text(
            f"# Field note — {name.replace('_', ' ')}\n\n{body}\n\nCategory: notes\n",
            encoding="utf-8",
        )
    return len(topics)


def main():
    print(f"crop_calendar: {write_crop_calendar()} rows")
    print(f"pest_disease_lookup: {write_pest_disease_lookup()} rows")
    print(f"fertilizer_guide: {write_fertilizer_guide()} rows")
    print(f"scheme_eligibility: {write_scheme_eligibility()} rows")
    print(f"market_prices: {write_market_prices()} rows")
    print(f"field_notes: {write_field_notes()} files")
    print("Re-run: python scripts/ingest_kb.py (notes add a few chunks)")


if __name__ == "__main__":
    main()
