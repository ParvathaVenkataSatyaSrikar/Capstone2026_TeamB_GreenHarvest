"""Field Officer portal home."""
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
require_permission("pages/20_Officer_Home.py")
role, _ = render_role_sidebar("Officer Home")
user = current_user()
meta = ROLE_META[role]
pending = len(get_pending_reviews())
kpis = get_kpis()

page_header(
    f"{meta['icon']} Field Officer Portal",
    f"Welcome, {user.get('display_name', 'Officer')} — Human-in-the-Loop quality control",
    role=role,
)

metric_row([
    ("Pending HITL", str(pending)),
    ("Open cases", str(kpis["open_escalations"])),
    ("Total queries", str(kpis["total_queries"])),
    ("AI", "Online" if get_chat_model() else "Offline"),
])

if pending:
    st.warning(f"**{pending}** farmer queries need your approval before they are released.")
else:
    st.success("No queries waiting for review.")

c1, c2 = st.columns(2)
with c1:
    if st.button("Human Review", type="primary", width="stretch"):
        st.switch_page("pages/4_Officer_Human_Review.py")
with c2:
    if st.button("Field Cases", width="stretch"):
        st.switch_page("pages/5_Officer_Field_Cases.py")
