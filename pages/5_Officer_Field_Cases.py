"""Field Officer portal — case management."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import streamlit as st
import pandas as pd
from src.ui.theme import bootstrap_app
from src.ui.components import apply_global_styles, page_header, metric_row
from src.ui.portal import render_role_sidebar
from src.auth.session import require_permission
from src.db.repository import list_cases, update_case, get_outbreak_alerts

bootstrap_app()
apply_global_styles()
require_permission("pages/5_Officer_Field_Cases.py")
role, _ = render_role_sidebar("Field Cases")

page_header("Field Cases", "Escalations, follow-ups and district alerts", role=role)

alerts = get_outbreak_alerts()
if alerts:
    st.error("District alerts active")
    for a in alerts:
        st.warning(f"**{a['district']}** — {a['message']}")

cases = list_cases()
open_cases = [c for c in cases if c.get("status") == "open"]
metric_row([
    ("Total cases", str(len(cases))),
    ("Open", str(len(open_cases))),
    ("Alerts", str(len(alerts))),
    ("Portal", "Field Officer"),
])

if not cases:
    st.info("No cases yet.")
    st.stop()

df = pd.DataFrame(cases)
cols = [c for c in ["case_id", "name", "district", "crop", "priority", "status", "review_status", "created_at"] if c in df.columns]
st.dataframe(df[cols], width="stretch", hide_index=True)

case_id = st.selectbox("Update case", [c["case_id"] for c in cases])
case = next(c for c in cases if c["case_id"] == case_id)

st.markdown(f"**AI summary:** {case.get('summary', 'N/A')}")
status = st.selectbox("Status", ["open", "in_progress", "resolved"], index=["open", "in_progress", "resolved"].index(case.get("status", "open")))
notes = st.text_area("Field visit notes", case.get("follow_up_notes") or "", height=100)
if st.button("Save case", type="primary"):
    update_case(case_id, status=status, follow_up_notes=notes)
    st.success("Case updated")
    st.rerun()
