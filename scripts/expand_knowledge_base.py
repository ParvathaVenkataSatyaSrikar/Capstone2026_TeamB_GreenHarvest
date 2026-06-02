"""Generate a large agriculture knowledge base (crops, diseases, pests, climates)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

KB = ROOT / "knowledge_base"

CROPS = {
    "cotton": {
        "season": "Kharif (June–July sowing)",
        "regions": "Telangana, Maharashtra, Gujarat, Punjab",
        "irrigation": "Critical at flowering and boll formation; avoid waterlogging.",
        "fertilizer": "Split NPK; avoid excess nitrogen late season.",
        "pests": "Pink bollworm, whitefly, aphids",
        "diseases": "Bacterial blight, alternaria leaf spot, root rot",
    },
    "wheat": {
        "season": "Rabi (Nov–Dec sowing)",
        "regions": "Punjab, Haryana, UP, MP",
        "irrigation": "Crown root, tillering, flowering — 4–6 irrigations typical.",
        "fertilizer": "120 kg N/ha split; zinc sulphate if deficient.",
        "pests": "Aphids, termites, armyworm",
        "diseases": "Yellow rust, loose smut, powdery mildew",
    },
    "paddy": {
        "season": "Kharif / Rabi depending on region",
        "regions": "AP, Telangana, West Bengal, Punjab",
        "irrigation": "Maintain 5 cm standing water in vegetative stage; drain before harvest.",
        "fertilizer": "Basal DAP + top dress urea at tillering and panicle initiation.",
        "pests": "Brown planthopper, stem borer, leaf folder",
        "diseases": "Blast, sheath blight, bacterial leaf blight",
    },
    "maize": {
        "season": "Kharif and Rabi",
        "regions": "Karnataka, AP, Bihar, Rajasthan",
        "irrigation": "Sensitive at knee-high and tasseling stages.",
        "fertilizer": "High nitrogen early; potassium at grain fill.",
        "pests": "Fall armyworm, stem borer",
        "diseases": "Turcicum leaf blight, maydis leaf blight",
    },
    "tomato": {
        "season": "Year-round in polyhouses; Kharif/Rabi open field",
        "regions": "Karnataka, AP, Maharashtra",
        "irrigation": "Drip preferred; avoid leaf wetness to reduce fungal disease.",
        "fertilizer": "Calcium nitrate to prevent blossom end rot.",
        "pests": "Fruit borer, whitefly, mites",
        "diseases": "Early blight, late blight, leaf curl virus",
    },
    "soybean": {
        "season": "Kharif",
        "regions": "MP, Maharashtra, Rajasthan",
        "irrigation": "Critical at pod formation; moisture stress reduces yield.",
        "fertilizer": "Rhizobium inoculation; moderate phosphorus.",
        "pests": "Girdle beetle, semilooper",
        "diseases": "Rust, yellow mosaic, charcoal rot",
    },
    "sugarcane": {
        "season": "12–18 month crop",
        "regions": "UP, Maharashtra, Karnataka",
        "irrigation": "Frequent irrigation; ratoon management important.",
        "fertilizer": "Heavy potassium; organic manure at planting.",
        "pests": "Top borer, pyrilla, termites",
        "diseases": "Red rot, smut, wilt",
    },
    "groundnut": {
        "season": "Kharif and summer",
        "regions": "Gujarat, AP, Tamil Nadu",
        "irrigation": "Light but regular; critical at pegging.",
        "fertilizer": "Gypsum at flowering; calcium for pod fill.",
        "pests": "Leaf miner, white grub",
        "diseases": "Tikka leaf spot, collar rot, aflatoxin risk if drought stress",
    },
    "chilli": {
        "season": "Kharif transplant",
        "regions": "AP, Telangana, Karnataka",
        "irrigation": "Drip; avoid water stress at flowering.",
        "fertilizer": "Balanced NPK; micronutrients for fruit set.",
        "pests": "Thrips, mites, fruit borer",
        "diseases": "Dieback, anthracnose, leaf curl",
    },
    "onion": {
        "season": "Rabi",
        "regions": "Maharashtra, Karnataka, MP",
        "irrigation": "Light frequent irrigations; stop before maturity.",
        "fertilizer": "High phosphorus at basal; nitrogen in splits.",
        "pests": "Thrips, onion maggot",
        "diseases": "Purple blotch, stemphylium blight",
    },
    "potato": {
        "season": "Rabi / short winters",
        "regions": "UP, Punjab, West Bengal",
        "irrigation": "Regular; critical at tuber bulking.",
        "fertilizer": "Potassium heavy; avoid green tubers at harvest.",
        "pests": "Aphids, cutworm",
        "diseases": "Late blight (Phytophthora), early blight",
    },
    "mustard": {
        "season": "Rabi",
        "regions": "Rajasthan, UP, Haryana",
        "irrigation": "2–3 irrigations if rainfall deficient.",
        "fertilizer": "Moderate nitrogen; sulphur improves oil content.",
        "pests": "Aphids, painted bug",
        "diseases": "White rust, alternaria blight",
    },
    "banana": {
        "season": "Perennial; planting year-round",
        "regions": "Tamil Nadu, Maharashtra, Gujarat",
        "irrigation": "High water requirement; drip with mulching.",
        "fertilizer": "Heavy potassium; magnesium if yellowing.",
        "pests": "Banana weevil, nematodes",
        "diseases": "Sigatoka leaf spot, Panama wilt",
    },
    "mango": {
        "season": "Perennial orchard crop",
        "regions": "UP, AP, Karnataka",
        "irrigation": "Drip; stress management for flowering.",
        "fertilizer": "Organic manure + NPK after harvest.",
        "pests": "Fruit fly, hoppers, mealybug",
        "diseases": "Powdery mildew, anthracnose, dieback",
    },
    "grapes": {
        "season": "Perennial",
        "regions": "Maharashtra, Karnataka, Tamil Nadu",
        "irrigation": "Controlled deficit at veraison in wine grapes.",
        "fertilizer": "Micronutrients boron and zinc for fruit set.",
        "pests": "Thrips, mealybug",
        "diseases": "Downy mildew, powdery mildew",
    },
    "bajra": {
        "season": "Kharif rainy season",
        "regions": "Rajasthan, Haryana, Gujarat",
        "irrigation": "Drought tolerant; one irrigation if prolonged dry spell.",
        "fertilizer": "Low nitrogen compared to maize.",
        "pests": "Shoot fly, stem borer",
        "diseases": "Downy mildew, ergot",
    },
    "chickpea": {
        "season": "Rabi",
        "regions": "MP, Rajasthan, Maharashtra",
        "irrigation": "Usually rainfed; one irrigation at flowering if dry.",
        "fertilizer": "Rhizobium; phosphorus important.",
        "pests": "Pod borer (Helicoverpa)",
        "diseases": "Wilt, blight, root rot",
    },
    "turmeric": {
        "season": "June planting",
        "regions": "Telangana, Tamil Nadu, Maharashtra",
        "irrigation": "Moist soil; mulching reduces weeds.",
        "fertilizer": "Organic manure + NPK splits.",
        "pests": "Rhizome scale, shoot borer",
        "diseases": "Rhizome rot, leaf spot",
    },
    "coffee": {
        "season": "Perennial shaded crop",
        "regions": "Karnataka, Kerala, Tamil Nadu",
        "irrigation": "Sprinkler in dry months.",
        "fertilizer": "Micronutrients on acidic soils.",
        "pests": "Coffee berry borer, white stem borer",
        "diseases": "Leaf rust, root diseases",
    },
}

CLIMATES = {
    "semi_arid": "Low rainfall 400–600 mm; focus on drought-tolerant crops (bajra, groundnut), mulching, and scheduled irrigation.",
    "humid_subtropical": "High humidity; fungal disease risk — prefer resistant varieties, avoid evening irrigation on foliage.",
    "tropical_wet": "Heavy monsoon; drainage essential for paddy and vegetables; pest pressure high in Kharif.",
    "temperate_hill": "Cool winters; suitable for potato, apple, off-season vegetables; frost protection needed.",
    "coastal": "Salt spray risk; choose tolerant varieties; leaching irrigation on saline patches.",
    "gangetic_plain": "Alluvial soils; excellent for wheat, paddy, sugarcane rotations.",
    "deccan_plateau": "Mixed red/black soils; cotton, sorghum, pulses common; micronutrient tests advised.",
}

DISEASE_TEMPLATES = [
    ("fungal_leaf_spot", "Circular brown spots with yellow halo; remove infected leaves; fungicide per local label."),
    ("bacterial_blight", "Water-soaked lesions turning dark; use clean seed; copper-based spray where approved."),
    ("rust", "Orange pustules on leaves; resistant variety; remove crop debris."),
    ("virus_mosaic", "Mottled leaves, stunting; control vector insects; rogue infected plants."),
    ("root_rot", "Wilting despite moisture; improve drainage; treat seed with fungicide."),
    ("nutrient_yellowing", "Interveinal chlorosis may indicate N, Fe, or Zn deficiency — soil test recommended."),
]


def write_crop(name: str, data: dict) -> Path:
    path = KB / "crops" / f"{name}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    body = f"""# {name.title()} — GreenHarvest crop guide

## Overview
- **Season:** {data['season']}
- **Major regions:** {data['regions']}

## Irrigation
{data['irrigation']}

## Fertilizer
{data['fertilizer']}

## Common pests
{data['pests']}

## Common diseases
{data['diseases']}

## Farmer tips
- Scout field weekly during vegetative and reproductive stages.
- Record spray dates and waiting periods before harvest.
- Contact KVK for variety-specific package of practices.
"""
    path.write_text(body, encoding="utf-8")
    return path


def write_disease(crop: str, disease_key: str, advice: str) -> Path:
    path = KB / "diseases" / f"{crop}_{disease_key}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"# {crop.title()} — {disease_key.replace('_', ' ')}\n\n"
        f"**Crop:** {crop}\n\n## Symptoms & management\n{advice}\n",
        encoding="utf-8",
    )
    return path


def write_climate(key: str, text: str) -> Path:
    path = KB / "climates" / f"{key}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"# Climate zone: {key.replace('_', ' ')}\n\n{text}\n", encoding="utf-8")
    return path


def main():
    count = 0
    for crop, data in CROPS.items():
        write_crop(crop, data)
        count += 1
        for dkey, advice in DISEASE_TEMPLATES:
            write_disease(crop, dkey, advice)
            count += 1
    for key, text in CLIMATES.items():
        write_climate(key, text)
        count += 1

    # Keep existing KB files; add market/scheme stubs if missing
    (KB / "market_faqs").mkdir(parents=True, exist_ok=True)
    mandi = KB / "market_faqs" / "mandi_prices.md"
    if not mandi.exists():
        mandi.write_text(
            "# Mandi price FAQs\n\nPrices vary daily by mandi. "
            "Check AGMARKNET or state portals. Compare nearby mandis before selling.\n",
            encoding="utf-8",
        )
        count += 1

    print(f"Wrote {count} knowledge base files under {KB}")
    print("Next: python scripts/ingest_kb.py")


if __name__ == "__main__":
    main()
