"""Farmer portal home."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import streamlit as st
from src.ui.theme import bootstrap_app
from src.ui.components import (
    apply_global_styles, page_header, metric_row, action_card,
    section_title, info_banner, feature_tile,
)
from src.ui.portal import render_role_sidebar, render_main_alerts
from src.ui.system_status import render_health_banner
from src.auth.session import require_permission, current_user, ROLE_META
from src.db.repository import get_farmer_kpis
from src.integrations.profile import list_profiles
from src.ui.farmer_insights import render_weather_alert_banner

bootstrap_app()
apply_global_styles()
require_permission("pages/10_Farmer_Home.py")
role, _ = render_role_sidebar("Farmer Home")
user = current_user()
meta = ROLE_META[role]

render_main_alerts(role)
render_health_banner(role)

page_header(
    f"Welcome back, {user.get('display_name', 'Farmer').split()[0]}",
    "Your farm command center — AI advice, expert review, schemes, and crop health in one place",
    role=role,
    image_key="hero_green",
)

farmer_id = user.get("farmer_id") or "—"
kpis = get_farmer_kpis(farmer_id) if farmer_id != "—" else {
    "queries_today": 0, "total_queries": 0, "avg_response_ms": 0, "pending_review": 0,
}
pending_idx = 2 if kpis.get("pending_review", 0) > 0 else None
metric_row([
    ("Total questions", str(kpis["total_queries"])),
    ("Asked today", str(kpis["queries_today"])),
    ("With expert", str(kpis["pending_review"])),
    ("Farm ID", farmer_id),
], highlight_index=pending_idx)

if farmer_id != "—":
    profs = [p for p in list_profiles() if p["farmer_id"] == farmer_id]
    if profs:
        render_weather_alert_banner(profs[0])

section_title("What do you need today?", "Choose a service — everything stays linked to your farm profile")

c1, c2 = st.columns(2, gap="medium")
with c1:
    action_card(
        "AI Crop Advisor",
        "Chat about pests, irrigation, fertilizer, market prices, and government schemes. Send photos for disease checks.",
        variant="green",
        emoji="🌱",
    )
    if st.button("Start conversation", type="primary", width="stretch", key="go_advisor"):
        st.switch_page("pages/2_Farmer_AI_Advisor.py")
with c2:
    action_card(
        "My Queries",
        "Your full history — instant AI answers and expert-reviewed replies in one timeline.",
        variant="teal",
        emoji="📋",
    )
    if st.button("View my history", width="stretch", key="go_queries"):
        st.switch_page("pages/3_Farmer_My_Queries.py")

section_title("Built for Indian farmers", "Trusted guides, weather context, and human experts when it matters")

col_a, col_b, col_c = st.columns(3, gap="medium")
_tiles = [
    ("card_crop_guides", "Trusted crop guides", "📚"),
    ("card_weather", "Weather-aware tips", "🌦️"),
    ("card_expert", "Expert review when needed", "👨‍🌾"),
]
for col, (key, caption, emoji) in zip((col_a, col_b, col_c), _tiles):
    with col:
        feature_tile(caption, image_key=key, emoji=emoji)

section_title("More services", "Schemes, dealers, and demo payment status")

c3, c4 = st.columns(2, gap="medium")
with c3:
    action_card(
        "Schemes & payments",
        "See eligible schemes and mock PM-KISAN installment status (demo only).",
        variant="gold",
        emoji="🏛️",
    )
    if st.button("Open schemes", width="stretch", key="go_schemes"):
        st.session_state["farmer_open_tab"] = "schemes"
        st.switch_page("pages/2_Farmer_AI_Advisor.py")
with c4:
    action_card(
        "Input dealers",
        "Licensed dealers near you and callback requests (demo directory).",
        variant="earth",
        emoji="🏪",
    )
    if st.button("Find dealers", width="stretch", key="go_dealers"):
        st.session_state["farmer_open_tab"] = "dealers"
        st.switch_page("pages/2_Farmer_AI_Advisor.py")

info_banner(
    "<strong>Instant answers</strong> for routine questions · "
    "<strong>Expert review</strong> for pests, insurance, and urgent cases · "
    "<strong>Photo diagnosis</strong> in Crop Advisor chat · "
    "<strong>Portal Assistant</strong> in the sidebar for application help"
)
