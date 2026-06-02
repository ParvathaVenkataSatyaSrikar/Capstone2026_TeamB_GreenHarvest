"""Test weather alerts, schemes, lifecycle, carbon."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.advisory.weather_alerts import get_weather_alerts
from src.advisory.scheme_recommender import recommend_schemes
from src.advisory.crop_lifecycle import get_lifecycle_context
from src.advisory.farm_insights import estimate_carbon_footprint


def main():
    w = get_weather_alerts("Guntur", "paddy")
    print("Weather:", w["title"], "—", w["farmer_message"][:60])

    profile = {"farmer_id": "F001", "district": "Warangal", "crop": "cotton", "land_acres": 3.5}
    schemes = recommend_schemes(profile)
    print("Schemes:", [s["scheme"] for s in schemes])

    lc = get_lifecycle_context("cotton", "flowering")
    print("Lifecycle:", lc["stage_label"], lc["advice"][:50])

    c = estimate_carbon_footprint("cotton", 3.5, "drip")
    print("Carbon:", c["kg_co2e_estimated"], "kg CO2e")
    print("\nOK")


if __name__ == "__main__":
    main()
