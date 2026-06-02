"""In-app alerts for farmers — pending review & newly approved answers."""
import streamlit as st
from src.db.repository import get_farmer_notification_summary, get_farmer_kpis


def _dismissed() -> set:
    if "dismissed_alert_ids" not in st.session_state:
        st.session_state.dismissed_alert_ids = set()
    return st.session_state.dismissed_alert_ids


def render_farmer_alerts(farmer_id: str, compact: bool = False) -> None:
    if not farmer_id:
        return
    summary = get_farmer_notification_summary(farmer_id)
    kpis = get_farmer_kpis(farmer_id)
    dismissed = _dismissed()

    pending = summary["pending"]
    approved = summary["recently_approved"]

    shown = False
    for item in pending:
        aid = f"pending_{item['interaction_id']}"
        if aid in dismissed:
            continue
        shown = True
        q = (item.get("query_text") or "")[:80]
        st.markdown(
            f'<div class="gh-alert gh-alert-warn">'
            f'<strong>⏳ Expert review in progress</strong><br>'
            f'<span>Your question about “{q}…” is with a field officer. '
            f'Check <b>My Queries</b> for the approved answer.</span></div>',
            unsafe_allow_html=True,
        )
        if st.button("Got it", key=f"dismiss_{aid}"):
            dismissed.add(aid)
            st.rerun()
        break

    for item in approved:
        aid = f"approved_{item['interaction_id']}"
        if aid in dismissed:
            continue
        if not shown or not compact:
            q = (item.get("query_text") or "")[:80]
            st.markdown(
                f'<div class="gh-alert gh-alert-success">'
                f'<strong>✅ Expert approved your answer</strong><br>'
                f'<span>“{q}…” — open <b>My Queries</b> or <b>AI Crop Advisor</b> history to read it.</span></div>',
                unsafe_allow_html=True,
            )
            if st.button("Thanks!", key=f"dismiss_{aid}"):
                dismissed.add(aid)
                st.rerun()
            shown = True
        break

    if not shown and kpis.get("pending_review", 0) > 0 and compact:
        st.markdown(
            f'<div class="gh-alert gh-alert-warn">'
            f'<strong>⏳ {kpis["pending_review"]} question(s)</strong> waiting for expert review — '
            f'see <b>My Queries</b>.</div>',
            unsafe_allow_html=True,
        )
