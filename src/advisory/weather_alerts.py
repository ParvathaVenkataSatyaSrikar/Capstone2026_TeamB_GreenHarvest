"""Weather alert system — heavy rain, heatwave, frost, storm (demo + CSV)."""
from __future__ import annotations

from src.integrations.weather import get_weather

ALERT_TYPES = ("heavy_rain", "heatwave", "frost", "storm", "drought_watch", "none")

_ALERT_COPY = {
    "heavy_rain": (
        "Heavy rain expected",
        "Rain expected soon. Avoid spraying pesticides today; ensure field drainage.",
    ),
    "heatwave": (
        "Heatwave alert",
        "High temperatures expected. Irrigate early morning or evening; avoid midday field work.",
    ),
    "frost": (
        "Frost warning",
        "Cold night risk. Protect nursery beds; delay sensitive sprays until temperatures rise.",
    ),
    "storm": (
        "Storm alert",
        "Strong winds or storms possible. Secure loose covers; postpone spraying and harvesting if unsafe.",
    ),
    "drought_watch": (
        "Dry spell watch",
        "Low rainfall forecast. Plan irrigation; mulch to conserve soil moisture.",
    ),
}


def _detect_from_forecast(forecast: str, temp_c: float, rainfall_mm: float) -> list[str]:
    f = (forecast or "").lower()
    alerts: list[str] = []
    if rainfall_mm >= 20 or any(w in f for w in ("heavy rain", "torrential", "very heavy")):
        alerts.append("heavy_rain")
    elif rainfall_mm >= 8 or any(w in f for w in ("moderate rain", "rain next", "showers")):
        if "heavy_rain" not in alerts:
            alerts.append("heavy_rain")
    if temp_c >= 38 or "heat" in f or "hot" in f:
        alerts.append("heatwave")
    if temp_c <= 4 or "frost" in f or "cold wave" in f:
        alerts.append("frost")
    if any(w in f for w in ("storm", "thunder", "cyclone", "gale", "wind")):
        alerts.append("storm")
    if any(w in f for w in ("dry", "drought")) or rainfall_mm == 0 and temp_c >= 32:
        if "drought_watch" not in alerts:
            alerts.append("drought_watch")
    return alerts


def get_weather_alerts(district: str, crop: str) -> dict:
    w = get_weather(district, crop)
    if not w.get("data_available", True):
        return {
            "district": district,
            "crop": crop,
            "primary_alert": "none",
            "title": "Weather data unavailable",
            "farmer_message": (
                w.get("message")
                or "Set your district in My farm to load demo weather for your area."
            ),
            "forecast_3day": "",
            "temp_c": None,
            "rainfall_mm": None,
            "all_alerts": [],
        }

    temp = float(w.get("temp_c", 0))
    rain = float(w.get("rainfall_mm", 0))
    forecast = str(w.get("forecast_3day", ""))
    csv_alert = str(w.get("alert", "none")).lower()

    detected = _detect_from_forecast(forecast, temp, rain)
    if csv_alert and csv_alert != "none" and csv_alert not in detected:
        detected.insert(0, csv_alert)

    if not detected:
        detected = ["none"]

    primary = detected[0] if detected[0] != "none" else "none"
    title, action = _ALERT_COPY.get(primary, ("All clear", "No severe weather alerts for your area today."))

    messages = []
    for a in detected:
        if a != "none" and a in _ALERT_COPY:
            t, msg = _ALERT_COPY[a]
            messages.append({"type": a, "title": t, "message": msg})

    return {
        "district": district,
        "crop": crop,
        "primary_alert": primary,
        "title": title,
        "farmer_message": action,
        "forecast_3day": forecast,
        "temp_c": temp,
        "rainfall_mm": rain,
        "all_alerts": messages,
    }
