"""Admin portal home."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import streamlit as st
from src.ui.theme import bootstrap_app
from src.ui.components import apply_global_styles, page_header, metric_row
from src.ui.portal import render_role_sidebar
from src.auth.session import require_permission, current_user, ROLE_META
from src.db.repository import get_kpis, get_pending_reviews
from src.chains.llm_factory import get_chat_model

bootstrap_app()
apply_global_styles()
require_permission("pages/30_Admin_Home.py")
role, _ = render_role_sidebar("Admin Home")
user = current_user()
meta = ROLE_META[role]
kpis = get_kpis()
pending = len(get_pending_reviews())

page_header(
    f"{meta['icon']} Admin Portal",
    f"Welcome, {user.get('display_name', 'Admin')} — analytics, governance, knowledge",
    role=role,
)

metric_row([
    ("Queries today", str(kpis["queries_today"])),
    ("Escalations", str(kpis["open_escalations"])),
    ("Pending HITL", str(pending)),
    ("AI", "Online" if get_chat_model() else "Offline"),
])

st.markdown("### Admin modules")
cols = st.columns(4)
pages = [
    ("Analytics", "pages/6_Admin_Analytics.py"),
    ("Human Review", "pages/4_Officer_Human_Review.py"),
    ("Governance", "pages/7_Admin_Governance.py"),
    ("Knowledge", "pages/8_Admin_Knowledge.py"),
]
for col, (label, path) in zip(cols, pages):
    with col:
        if st.button(label, width="stretch"):
            st.switch_page(path)

if st.button("Settings", width="content"):
    st.switch_page("pages/9_Admin_Settings.py")
