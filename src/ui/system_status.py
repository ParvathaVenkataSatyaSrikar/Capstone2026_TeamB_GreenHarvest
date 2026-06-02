"""System health banner — Streamlit status indicators."""
from __future__ import annotations

import streamlit as st

from config.settings import get_settings
from src.resilience.network import is_online
from src.integrations.tavily_search import tavily_available
from src.resilience.llm_router import get_last_provider, probe_providers
from src.rag.retriever import get_active_embedding_provider


def get_health_summary() -> dict:
    from config.settings import get_settings as _get_settings

    cached = st.session_state.get("_gh_health_summary")
    if cached:
        return cached
    settings = _get_settings()
    online = is_online()
    has_llm = bool(settings.gemini_api_key)
    store = get_active_embedding_provider()
    summary = {
        "online": online,
        "has_llm": has_llm,
        "rag_store": store,
        "faiss_ready": store == "faiss_gemini",
        "tavily": tavily_available(),
        "llm_provider": get_last_provider(),
    }
    st.session_state["_gh_health_summary"] = summary
    return summary


def render_health_banner(role: str = "farmer", show_admin_detail: bool = False) -> None:
    """User-facing alerts by role — technical ops messages only for admin."""
    h = get_health_summary()

    if role == "farmer":
        if not h["online"]:
            st.warning(
                "**You are offline** — we will use saved crop guides on this device. "
                "Reconnect to the internet for the fullest answers."
            )
        return

    if role == "field_officer":
        if not h["online"]:
            st.warning("**Offline** — farmer answers may use saved guides until you reconnect.")
        elif not h["has_llm"]:
            st.warning("**AI not configured** — contact your admin if answers look incomplete.")
        return

    # Admin / developer-facing
    if not h["online"]:
        st.warning(
            "**No internet** — answers use saved crop guides on this device. "
            "Reconnect for full AI replies."
        )
        return

    if not h["has_llm"]:
        st.warning(
            "**AI keys not set** — using local crop guides only. "
            "Add `GEMINI_API_KEY` in `.env` and run `python scripts/ingest_kb.py`."
        )
        return

    if h["rag_store"] == "keyword":
        st.info(
            "**Guide search mode (keyword)** — run `python scripts/ingest_kb.py` with a valid "
            "`GEMINI_API_KEY` for full FAISS vector search."
        )

    if show_admin_detail and role == "admin":
        with st.expander("System health (admin)", expanded=False):
            st.write(f"Network: {'Online' if h['online'] else 'Offline'}")
            st.write(f"RAG store: `{h['rag_store']}`")
            st.write(f"Last LLM: `{h['llm_provider']}`")
            st.write(f"Tavily: {'on' if h['tavily'] else 'off'}")
            if st.button("Refresh provider probe", key="probe_health"):
                for name, state in probe_providers().items():
                    st.write(f"- **{name}**: {state}")
