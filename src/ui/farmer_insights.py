"""Farmer dashboard widgets — weather alerts, schemes, lifecycle, sustainability."""
from __future__ import annotations

import streamlit as st

from src.advisory.weather_alerts import get_weather_alerts
from src.advisory.scheme_recommender import recommend_schemes
from src.advisory.crop_lifecycle import get_lifecycle_context, LIFECYCLE_STAGES
from src.advisory.farm_insights import (
    cost_optimization_tips,
    sustainable_farming_tips,
    estimate_carbon_footprint,
)


def render_weather_alert_banner(profile: dict) -> None:
    district = profile.get("district", "")
    crop = profile.get("crop", "")
    alerts = get_weather_alerts(district, crop)
    primary = alerts.get("primary_alert", "none")
    if primary == "none":
        st.success(f"🌤️ {alerts['farmer_message']}")
        return
    icon = {"heavy_rain": "🌧️", "heatwave": "🌡️", "frost": "❄️", "storm": "⛈️"}.get(primary, "⚠️")
    st.warning(f"{icon} **{alerts['title']}** — {alerts['farmer_message']}")
    for a in alerts.get("all_alerts", [])[1:3]:
        st.caption(f"Also: {a['title']} — {a['message']}")


def render_scheme_cards(profile: dict) -> None:
    schemes = recommend_schemes(profile)[:4]
    for s in schemes:
        with st.container(border=True):
            st.markdown(f"**{s['scheme']}**")
            st.caption(s["reason"])
            st.write(s["benefit"])
            if s.get("demo_status"):
                st.info(f"Demo status: {s['demo_status']}")
            st.caption(f"Next step: {s['action']}")


def render_lifecycle_card(profile: dict) -> None:
    ctx = get_lifecycle_context(profile.get("crop", ""), profile.get("crop_stage", ""))
    st.metric("Growth stage", ctx["stage_label"])
    st.write(ctx["advice"])
    st.caption("Stages: " + " → ".join(LIFECYCLE_STAGES))


def render_sustainability_panel(profile: dict) -> None:
    crop = profile.get("crop", "")
    acres = float(profile.get("land_acres") or 1)
    irr = profile.get("irrigation_type", "")
    carbon = estimate_carbon_footprint(crop, acres, irr)
    st.metric("Carbon estimate (demo)", f"{carbon['kg_co2e_estimated']} kg CO2e")
    st.caption(carbon["disclaimer"])
    st.markdown("**Cost tips**")
    for t in cost_optimization_tips(crop)[:3]:
        st.write(f"- {t}")
    st.markdown("**Sustainable practices**")
    for t in sustainable_farming_tips(crop, irr)[:3]:
        st.write(f"- {t}")
    st.markdown("**Lower footprint**")
    for t in carbon["reduction_tips"]:
        st.write(f"- {t}")
