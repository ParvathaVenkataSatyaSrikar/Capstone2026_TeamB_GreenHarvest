"""Admin portal — governance."""
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
from src.db.repository import get_audit_logs

bootstrap_app()
apply_global_styles()
require_permission("pages/7_Admin_Governance.py")
role, _ = render_role_sidebar("Governance")

page_header("Governance & Audit", "Full traceability of every Gen AI decision", role=role)

logs = get_audit_logs(300)
metric_row([
    ("Audit events", str(len(logs))),
    ("Compliance", "Enabled"),
    ("Guardrails", "Active"),
    ("HITL", "Required for risk"),
])

if logs:
    df = pd.DataFrame(logs)
    st.dataframe(df[["created_at", "user_role", "action", "model_used", "confidence", "guardrail_triggered"]], hide_index=True)
    st.download_button("Export audit log", df.to_csv(index=False), "audit.csv", mime="text/csv")
else:
    st.info("No audit logs yet.")

st.markdown("""
**Governance controls**
- Every query logged with model, confidence, and sources  
- Guardrails block unsafe pesticide or diagnosis claims  
- Low-confidence answers routed to human experts  
- Staff approval required before farmer sees sensitive guidance  
""")
