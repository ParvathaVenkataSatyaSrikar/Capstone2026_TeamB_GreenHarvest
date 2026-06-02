"""Admin portal — settings."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import streamlit as st
from config.settings import get_settings
from src.ui.theme import bootstrap_app
from src.ui.components import apply_global_styles, page_header, section_card, end_card
from src.ui.portal import render_role_sidebar
from src.auth.session import require_permission
from src.db.repository import reset_demo_data
from src.rag.retriever import ingest_knowledge_base, get_active_embedding_provider, load_kb_documents
from src.ui.system_status import render_health_banner
from src.chains.llm_factory import get_chat_model
from src.resilience.llm_router import probe_providers, get_last_provider
from src.resilience.network import is_online
from langchain_core.messages import HumanMessage

bootstrap_app()
apply_global_styles()
require_permission("pages/9_Admin_Settings.py")
role, _ = render_role_sidebar("Settings")

page_header("System Settings", "OpenAI + Gemini + RAG + vision", role=role)
render_health_banner(role, show_admin_detail=True)

s = get_settings()

section_card("API keys")
st.write(f"**OpenAI:** {'Configured' if s.openai_api_key else 'Missing'} · model `{s.openai_model}`")
st.write(f"**Gemini:** {'Configured' if s.gemini_api_key else 'Missing'} · model `{s.gemini_model}`")
st.write(f"**Tavily:** {'Configured' if s.tavily_api_key else 'Optional'}")
st.caption(f"Fallback order: **{s.llm_provider}** → OpenAI → Gemini → offline KB · timeout {s.llm_request_timeout_sec}s")
end_card()

section_card("Test connections")
if st.button("Test all LLM APIs", type="primary"):
    status = probe_providers()
    for name, state in status.items():
        icon = "✅" if str(state).startswith("ok") else ("⚠️" if state in ("no_key", "offline_network", "ready") else "❌")
        st.write(f"{icon} **{name}**: {state}")
if st.button("Test chat (resilient router)"):
    llm = get_chat_model()
    r = llm.invoke([HumanMessage(content="Reply: GreenHarvest online.")])
    meta = getattr(r, "response_metadata", {}) or {}
    st.success(f"{getattr(r, 'content', r)}  (provider: {meta.get('provider', get_last_provider())})")
end_card()

section_card("RAG knowledge base")
st.write(f"**Chunks loaded:** {len(load_kb_documents())}")
st.write(f"**Embedding store:** {get_active_embedding_provider()}")
st.write(f"**Network:** {'Online' if is_online() else 'Offline'}")
if st.button("Re-ingest knowledge base"):
    n = ingest_knowledge_base()
    st.success(f"Ingested {n} chunks")
if st.button("Expand KB files (script)"):
    st.code("python scripts/expand_knowledge_base.py\npython scripts/ingest_kb.py", language="powershell")
end_card()

section_card("Automated tests")
st.caption("Run from the project root (same folder as app.py):")
st.code(
    "python scripts/test_apis.py\npython tests/test_llm_providers.py\n"
    "python tests/test_rag.py\npython tests/test_vision.py",
    language="powershell",
)
end_card()

section_card("Demo data")
if st.button("Reset database"):
    reset_demo_data()
    st.success("Database reset.")
end_card()
