"""Farmer portal — query history."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import streamlit as st
from src.ui.theme import bootstrap_app
from src.ui.components import apply_global_styles, page_header, render_response_box
from src.ui.portal import render_role_sidebar, render_main_alerts
from src.ui.farmer_copy import render_review_status, friendly_intent, explain_escalation_reason, REVIEW_EXPLAIN
from src.ui.trace_utils import escalation_from_row
from src.auth.session import require_permission, current_user
from src.db.repository import get_interactions

bootstrap_app()
apply_global_styles()
require_permission("pages/3_Farmer_My_Queries.py")
role, _ = render_role_sidebar("My Queries")
render_main_alerts(role)

user = current_user()
farmer_id = user.get("farmer_id")
if not farmer_id:
    st.error("Your account is not linked to a farmer profile.")
    st.stop()

page_header(
    "My Queries",
    "Every question you asked — instant answers, expert reviews, and approvals in one place",
    role=role,
    image_key="hero_fields",
)

rows = get_interactions(farmer_id=farmer_id, limit=40)
if not rows:
    st.info("No queries yet. Go to **AI Crop Advisor** to ask your first question.")
    if st.button("Open AI Crop Advisor", type="primary"):
        st.switch_page("pages/2_Farmer_AI_Advisor.py")
    st.stop()

pending = sum(1 for r in rows if r.get("review_status") == "pending_human")
approved = sum(1 for r in rows if r.get("review_status") in ("auto_approved", "approved"))
c1, c2, c3 = st.columns(3)
c1.metric("Total", len(rows))
c2.metric("Answered", approved)
c3.metric("With expert", pending, delta=None if pending == 0 else "waiting")

st.markdown("### Your questions")
for row in rows[:12]:
    status = row.get("review_status") or "auto_approved"
    info = REVIEW_EXPLAIN.get(status, REVIEW_EXPLAIN["auto_approved"])
    label = row["query_text"][:70] + ("…" if len(row["query_text"]) > 70 else "")
    with st.expander(f"{info['icon']} {row['created_at']} — {label}", expanded=(status == "pending_human")):
        render_review_status(status, escalation_from_row(row))
        if row.get("intent"):
            st.caption(f"Topic: **{friendly_intent(row['intent'])}**")
        if status == "pending_human":
            st.warning(explain_escalation_reason(escalation_from_row(row)))
        render_response_box(
            row.get("response_text") or "Waiting for expert approval — check back soon.",
            pending=(status == "pending_human"),
        )
