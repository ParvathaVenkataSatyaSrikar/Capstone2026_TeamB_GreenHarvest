"""Admin portal — analytics."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import streamlit as st
import plotly.express as px
from src.ui.theme import bootstrap_app
from src.ui.components import apply_global_styles, page_header, metric_row
from src.ui.portal import render_role_sidebar
from src.auth.session import require_permission
from src.analytics.trends import (
    get_intent_distribution, get_district_activity,
    get_escalation_rate, get_confidence_series, check_outbreak_patterns,
)
from src.db.repository import get_outbreak_alerts, get_kpis, resolve_outbreak_alert

bootstrap_app()
apply_global_styles()
require_permission("pages/6_Admin_Analytics.py")
role, _ = render_role_sidebar("Analytics")

page_header("Analytics & Early Warning", "District trends, AI performance and pest cluster detection", role=role)

kpis = get_kpis()
metric_row([
    ("Queries today", str(kpis["queries_today"])),
    ("Total", str(kpis["total_queries"])),
    ("Escalation %", f"{get_escalation_rate()}%"),
    ("Open cases", str(kpis["open_escalations"])),
])

if st.button("Run pest outbreak detection", type="primary"):
    new = check_outbreak_patterns()
    st.success(f"Created {len(new)} new alert(s)" if new else "No new outbreaks")

c1, c2 = st.columns(2)
with c1:
    intent_df = get_intent_distribution()
    if not intent_df.empty:
        st.plotly_chart(px.pie(intent_df, values="count", names="intent", title="Query types"), width="stretch")
with c2:
    conf_df = get_confidence_series()
    if not conf_df.empty:
        st.plotly_chart(px.histogram(conf_df, x="confidence", nbins=12, title="AI confidence"), width="stretch")

district_df = get_district_activity()
if not district_df.empty:
    st.plotly_chart(px.bar(district_df, x="district", y="count", color="intent", title="Activity by district"), width="stretch")

st.markdown("### Outbreak alerts")
st.caption(
    "Early warning only: counts pest/disease questions by district and profile crop (last 7 days). "
    "Not a confirmed outbreak — officers should verify."
)
for a in get_outbreak_alerts(active_only=False):
    c1, c2 = st.columns([5, 1])
    with c1:
        st.write(f"- [{a['status']}] **{a['district']}**: {a['message']}")
    with c2:
        if a.get("status") == "active" and st.button("Resolve", key=f"resolve_alert_{a['alert_id']}"):
            resolve_outbreak_alert(int(a["alert_id"]))
            st.rerun()
