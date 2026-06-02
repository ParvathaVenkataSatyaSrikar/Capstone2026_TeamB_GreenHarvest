"""Mock soil report service."""
from __future__ import annotations

import pandas as pd

from config.settings import DATA_DIR

_soil_df: pd.DataFrame | None = None


def _load() -> pd.DataFrame:
    global _soil_df
    if _soil_df is None:
        path = DATA_DIR / "soil_reports.csv"
        _soil_df = pd.read_csv(path) if path.exists() else pd.DataFrame()
    return _soil_df


def get_soil_report(farmer_id: str, district: str, crop: str) -> dict:
    df = _load()
    district = (district or "").strip()
    crop = (crop or "").strip().lower()
    if df.empty:
        return {
            "ph": 7.0,
            "recommendation": "General district soil — test recommended",
            "data_available": False,
        }
    row = df[df["farmer_id"] == farmer_id].head(1)
    if row.empty and district and crop:
        row = df[
            (df["district"].str.lower() == district.lower()) & (df["crop"].str.lower() == crop)
        ].head(1)
    if row.empty and district:
        row = df[df["district"].str.lower() == district.lower()].head(1)
    if row.empty:
        return {
            "ph": 7.0,
            "nitrogen": "medium",
            "phosphorus": "medium",
            "potassium": "medium",
            "organic_carbon": 0.4,
            "recommendation": f"No soil lab row for {district} — schedule a Soil Health Card test.",
            "data_available": False,
        }
    r = row.iloc[0]
    return {
        "ph": float(r.get("ph", 7)),
        "nitrogen": str(r.get("nitrogen", "medium")),
        "phosphorus": str(r.get("phosphorus", "medium")),
        "potassium": str(r.get("potassium", "medium")),
        "organic_carbon": float(r.get("organic_carbon", 0.4)),
        "recommendation": str(r.get("recommendation", "")),
        "district": str(r.get("district", district)),
        "crop": str(r.get("crop", crop)),
        "data_available": True,
    }


def format_soil_answer(farmer_id: str, district: str, crop: str) -> str:
    """Soil health summary from simulated soil_reports.csv."""
    s = get_soil_report(farmer_id, district, crop)
    if not s.get("data_available"):
        return (
            f"**Soil health ({district or 'your area'})**\n\n"
            f"{s.get('recommendation', 'No soil report on file.')}\n\n"
            "Visit your block agriculture office for a **Soil Health Card** test."
        )
    lines = [
        f"**Soil report — {s.get('district', district)} ({s.get('crop', crop).title()})**",
        f"- **pH:** {s['ph']:.1f}",
        f"- **Nitrogen (N):** {s['nitrogen']}",
        f"- **Phosphorus (P):** {s['phosphorus']}",
        f"- **Potassium (K):** {s['potassium']}",
        f"- **Organic carbon:** {s.get('organic_carbon', 0):.2f}%",
        f"- **Recommendation:** {s['recommendation']}",
        "\n*Demo soil data from data/soil_reports.csv — confirm with a lab test before major fertilizer changes.*",
    ]
    return "\n".join(lines)
