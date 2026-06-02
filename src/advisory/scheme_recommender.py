"""Government scheme recommender — location, crop, land size."""
from __future__ import annotations

from src.integrations.scheme_payment import get_mock_scheme_status


def recommend_schemes(profile: dict) -> list[dict]:
    district = (profile.get("district") or "").strip()
    crop = (profile.get("crop") or "").strip().lower()
    acres = float(profile.get("land_acres") or profile.get("land_size") or 0)
    farmer_id = profile.get("farmer_id", "F001")
    dl = district.lower()

    schemes: list[dict] = []

    schemes.append({
        "scheme": "PM-KISAN",
        "eligible": acres > 0 or True,
        "benefit": "₹6,000/year in 3 installments (₹2,000 each)",
        "reason": "Small and marginal farmers with cultivable land are typically eligible.",
        "action": "Check Aadhaar-linked bank account on PM-KISAN portal or visit CSC.",
    })

    if crop in {"paddy", "rice", "wheat", "cotton", "sugarcane"}:
        schemes.append({
            "scheme": "PMFBY (Crop Insurance)",
            "eligible": True,
            "benefit": "Yield loss protection (premium subsidized)",
            "reason": f"{crop.title()} is covered under notified areas — confirm local notification.",
            "action": "Enroll before sowing cutoff via bank/CSC/insurance intermediary.",
        })

    if acres >= 2:
        schemes.append({
            "scheme": "KCC (Kisan Credit Card)",
            "eligible": True,
            "benefit": "Seasonal crop loan at subsidized interest",
            "reason": f"Land holding ~{acres} acres supports credit need for inputs.",
            "action": "Apply at your primary agriculture cooperative bank.",
        })

    if "warangal" in dl or "telangana" in dl:
        schemes.append({
            "scheme": "Telangana Rythu Bandhu",
            "eligible": True,
            "benefit": "Investment support per acre per season (state rules)",
            "reason": "Telangana farmers with pattadar passbook.",
            "action": "Verify eligibility on state agriculture portal.",
        })
    elif "punjab" in dl or "haryana" in dl or "jalandhar" in dl:
        schemes.append({
            "scheme": "State input subsidy (Punjab/Haryana)",
            "eligible": True,
            "benefit": "Subsidized seed/fertilizer via POS",
            "reason": "Wheat/paddy belt state programs.",
            "action": "Buy from licensed dealer with farmer ID.",
        })
    elif "maharashtra" in dl or "nashik" in dl or "akola" in dl:
        schemes.append({
            "scheme": "Maharashtra farm schemes",
            "eligible": True,
            "benefit": "Horticulture and drip subsidy programs (crop dependent)",
            "reason": f"District {district} — tomato/soybean/cotton programs vary.",
            "action": "Contact district agriculture officer.",
        })

    if crop in {"tomato", "chilli", "onion", "grapes"}:
        schemes.append({
            "scheme": "Horticulture Mission / MIDH",
            "eligible": True,
            "benefit": "Greenhouse, drip, post-harvest support (component based)",
            "reason": "Horticulture crop detected.",
            "action": "Apply via state horticulture department.",
        })

    status_rows = {r["scheme"].split("(")[0].strip(): r for r in get_mock_scheme_status(farmer_id, district)}
    for s in schemes:
        key = s["scheme"].split("(")[0].strip()
        for k, row in status_rows.items():
            if k in s["scheme"] or s["scheme"].startswith(k):
                s["demo_status"] = row.get("status", "")
                break

    return schemes


def format_schemes_for_prompt(schemes: list[dict]) -> str:
    if not schemes:
        return "No scheme matches."
    lines = []
    for s in schemes[:6]:
        lines.append(
            f"- {s['scheme']}: {s['benefit']} | Eligible: {s['eligible']} | "
            f"{s['reason']} → {s['action']}"
        )
    return "\n".join(lines)
