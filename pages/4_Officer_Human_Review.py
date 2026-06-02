"""Field Officer portal — Human-in-the-Loop review."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import streamlit as st
from src.ui.theme import bootstrap_app
from src.ui.components import apply_global_styles, page_header, section_card, end_card, metric_row
from src.ui.portal import render_role_sidebar
from src.auth.session import require_permission, current_user
from src.services.hitl_service import list_pending_for_review, staff_approve, staff_reject
from src.db.repository import list_cases

bootstrap_app()
apply_global_styles()
require_permission("pages/4_Officer_Human_Review.py")
role, _ = render_role_sidebar("Human Review")

page_header("Human Review", "Approve AI drafts before farmers receive sensitive guidance", role=role)

pending = list_pending_for_review()
metric_row([
    ("Pending", str(len(pending))),
    ("Your role", "Expert reviewer"),
    ("Action", "Approve / Edit / Reject"),
    ("Support", "AI-assisted drafts"),
])

if not pending:
    st.success("All clear — no queries waiting for human review.")
    st.balloons()
    st.stop()

for idx, item in enumerate(pending[:5]):
    with st.container(border=True):
        st.markdown(f"#### Case #{item['interaction_id']} — {item['name']}")
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            st.markdown(f"**Farmer asked:** {item['query_text']}")
            st.caption(f"{item['district']} · {item['crop']} · Intent: {item.get('intent', 'N/A')}")
        with c2:
            st.metric("AI confidence", f"{item.get('confidence', 0)}")
        with c3:
            st.caption("Review required")

        default_text = item.get("draft_response") or ""
        edited = st.text_area("Edit response for farmer", value=default_text, height=160, key=f"edit_{item['interaction_id']}")

        case = next((c for c in list_cases() if c.get("interaction_id") == item["interaction_id"]), None)
        case_id = case["case_id"] if case else None

        b1, b2, b3 = st.columns(3)
        with b1:
            if st.button("Approve & send", type="primary", key=f"ok_{idx}", width="stretch"):
                reviewer = current_user().get("display_name") or current_user().get("username", role)
                staff_approve(item["interaction_id"], edited, reviewer, case_id)
                st.success("Sent to farmer")
                st.rerun()
        with b2:
            if st.button("Reject", key=f"no_{idx}", width="stretch"):
                reviewer = current_user().get("display_name") or current_user().get("username", role)
                staff_reject(item["interaction_id"], reviewer, case_id)
                st.rerun()
        with b3:
            st.caption("Human-in-the-Loop keeps farmers safe")
