"""Mock weather service from CSV."""
from __future__ import annotations

import pandas as pd

from config.settings import DATA_DIR

_weather_df: pd.DataFrame | None = None


def _load() -> pd.DataFrame:
    global _weather_df
    if _weather_df is None:
        path = DATA_DIR / "weather.csv"
        _weather_df = pd.read_csv(path) if path.exists() else pd.DataFrame()
    return _weather_df


def get_weather(district: str, crop: str) -> dict:
    df = _load()
    district = (district or "").strip()
    crop = (crop or "").strip().lower()
    if df.empty:
        return {
            "district": district,
            "crop": crop,
            "alert": "none",
            "message": "No weather data file",
            "data_available": False,
        }
    mask = (df["district"].str.lower() == district.lower()) & (df["crop"].str.lower() == crop)
    row = df[mask].head(1)
    if row.empty and district:
        row = df[df["district"].str.lower() == district.lower()].head(1)
    if row.empty:
        return {
            "district": district,
            "crop": crop,
            "alert": "none",
            "message": f"No weather row for {district} — add district in My farm or expand weather.csv",
            "data_available": False,
        }
    r = row.iloc[0]
    return {
        "district": str(r["district"]),
        "crop": str(r["crop"]),
        "date": str(r.get("date", "")),
        "temp_c": float(r.get("temp_c", 0)),
        "humidity_pct": float(r.get("humidity_pct", 0)),
        "rainfall_mm": float(r.get("rainfall_mm", 0)),
        "forecast_3day": str(r.get("forecast_3day", "")),
        "alert": str(r.get("alert", "none")),
        "data_available": True,
    }


def format_weather_answer(district: str, crop: str) -> str:
    """Full weather + alert text from simulated CSV (same path as tool_get_weather)."""
    from src.advisory.weather_alerts import get_weather_alerts

    w = get_weather(district, crop)
    if not w.get("data_available"):
        return (
            f"**Weather update ({district or 'your area'})**\n\n"
            f"{w.get('message', 'Weather data not found.')}\n\n"
            "Set your **district** in **My farm** to match a row in GreenHarvest demo weather data."
        )

    alerts = get_weather_alerts(district, crop)
    lines = [
        f"**Weather — {w['district']} ({w['crop'].title()})**",
        f"- **Date (demo):** {w.get('date', 'today')}",
        f"- **Temperature:** {w['temp_c']:.0f} °C",
        f"- **Humidity:** {w['humidity_pct']:.0f}%",
        f"- **Rainfall (recent):** {w['rainfall_mm']:.0f} mm",
        f"- **3-day outlook:** {w['forecast_3day']}",
        f"- **Alert level:** {w.get('alert', 'none').replace('_', ' ').title()}",
        "",
        f"**Advisory:** {alerts['title']}",
        alerts["farmer_message"],
    ]
    extra = alerts.get("all_alerts") or []
    if len(extra) > 1:
        lines.append("\n**All active alerts:**")
        for a in extra:
            lines.append(f"- {a['title']}: {a['message']}")
    lines.append("\n*Demo weather from data/weather.csv — check IMD/local forecast before field work.*")
    return "\n".join(lines)
