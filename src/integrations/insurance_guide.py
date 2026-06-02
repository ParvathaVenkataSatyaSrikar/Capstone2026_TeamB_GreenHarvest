"""Crop insurance (PMFBY) claim guidance — demo steps + scheme status."""
from __future__ import annotations

from src.advisory.scheme_recommender import recommend_schemes
from src.integrations.scheme_payment import get_mock_scheme_status


def format_insurance_answer(
    farmer_id: str,
    district: str,
    crop: str,
    query: str = "",
) -> str:
    """How to file crop insurance / PMFBY claim (e.g. after rainfall)."""
    profile = {"farmer_id": farmer_id, "district": district, "crop": crop}
    schemes = recommend_schemes(profile)
    pmfby = next(
        (s for s in schemes if "PMFBY" in s.get("scheme", "") or "Insurance" in s.get("scheme", "")),
        None,
    )
    lower = (query or "").lower()
    after_rain = any(k in lower for k in ("rain", "rainfall", "flood", "cyclone", "storm", "hail"))

    lines = [
        "**Crop insurance — how to file a claim (demo guide)**",
        "",
        f"**Your question:** {query.strip() or 'Crop insurance claim process'}",
        f"**Profile context:** {crop.title()} in {district or 'your district'}",
        "",
    ]
    if after_rain:
        lines.append(
            "You asked about filing insurance **after rainfall** — this is a **claim / loss intimation** "
            "process, not a daily weather report."
        )
        lines.append("")

    lines.extend([
        "**Steps (PMFBY-style — confirm on pmfby.gov.in or your bank/CSC):**",
        "1. **Intimate loss early** — often within **72 hours** of the event (check your policy / local notification).",
        "2. Keep **policy / enrollment receipt**, land records, and **sowing certificate** ready.",
        "3. **Photograph** affected plots with date; note village, survey number, and crop stage.",
        "4. Report to **bank branch, CSC, or insurer** listed on your policy — do not wait for weather to clear only.",
        "5. District may order **CCE (crop cutting experiment)** or survey — cooperate with agriculture department staff.",
        "6. Submit claim form, ID, passbook copy, and photos; track status on portal or through bank.",
        "7. Payout uses **notified yield vs assessed loss** — timelines vary by state and season.",
        "",
    ])

    if pmfby:
        lines.extend([
            f"**Enrollment ({district}):** {pmfby.get('reason', '')}",
            f"**Action:** {pmfby.get('action', '')}",
            "",
        ])
    else:
        lines.append(
            f"**Note:** {crop.title()} may need local **PMFBY notification** in {district or 'your district'} — "
            "ask the agriculture office if the crop is covered this season."
        )
        lines.append("")

    status = get_mock_scheme_status(farmer_id, district)
    lines.append("**Your demo scheme status (payments / enrollment awareness):**")
    for row in status[:2]:
        lines.append(f"- **{row['scheme']}:** {row['status']} (ref {row.get('reference', '—')})")

    lines.append(
        "\n*GreenHarvest does not file real claims. Use the official PMFBY portal, insurer, or CSC. "
        "For complex disputes, a field officer review is recommended.*"
    )
    return "\n".join(lines)
