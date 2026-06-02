"""Portal layout — sidebar navigation, alerts, and Portal Assistant."""
import streamlit as st
from src.auth.session import (
    init_auth_state, current_user, current_role,
    logout_user, ROLE_META, require_login,
)
from src.auth.rbac import ROLE_NAV


def render_main_nav_bar(role: str) -> None:
    """Top navigation on main page — always visible when sidebar is collapsed."""
    items = ROLE_NAV.get(role, [])
    if not items:
        return
    st.markdown(
        '<div class="gh-nav-hint">'
        "Use the menu below or the <b>sidebar</b> to move between pages "
        "(click <b>►</b> top-left if the sidebar is hidden)."
        "</div>",
        unsafe_allow_html=True,
    )
    cols = st.columns(len(items))
    for col, (path, title, icon) in zip(cols, items):
        with col:
            st.page_link(path, label=f"{icon} {title}")
from src.ui.components import sidebar_brand, status_bar
from src.ui.guide_chat import render_guide_sidebar_button
from src.ui.notifications import render_farmer_alerts
from src.ui.branding import GUIDE_SHORT
from src.i18n.language import (
    SUPPORTED_LANGUAGES, LANGUAGE_LABELS, normalize_language,
    persist_farmer_language,
)


def _init_language_from_profile(user: dict) -> None:
    """On first load after login, use farmer profile preferred language."""
    if st.session_state.get("_language_loaded"):
        return
    farmer_id = user.get("farmer_id")
    if farmer_id:
        from src.integrations.profile import get_profile
        profile = get_profile(farmer_id) or {}
        if profile.get("language"):
            st.session_state.portal_language = normalize_language(profile["language"])
    st.session_state._language_loaded = True


def render_role_sidebar(page_name: str = "") -> tuple[str, str]:
    require_login()
    init_auth_state()
    user = current_user() or {}
    role = current_role()
    if role not in ROLE_META:
        st.error("Session error — please log out and sign in again.")
        if st.sidebar.button("Go to Login"):
            logout_user()
            st.switch_page("pages/0_Login.py")
        st.stop()
    meta = ROLE_META[role]

    sidebar_brand(meta["color"], meta["icon"], meta["label"], user.get("display_name", ""))

    st.sidebar.caption(
        "💡 If you hide this panel, click the **►** arrow at the **top-left** of the page to show it again."
    )

    st.sidebar.markdown("##### 🧭 Menu")
    for path, title, icon in ROLE_NAV.get(role, []):
        st.sidebar.page_link(path, label=f"{icon} {title}")

    st.sidebar.markdown("---")
    _init_language_from_profile(user)
    if "portal_language" not in st.session_state:
        st.session_state.portal_language = "english"
    prev_lang = normalize_language(st.session_state.portal_language)
    st.session_state.portal_language = prev_lang

    language = st.sidebar.selectbox(
        "🗣️ Answer language",
        options=SUPPORTED_LANGUAGES,
        format_func=lambda code: LANGUAGE_LABELS.get(code, code),
        key="portal_language",
        help="AI replies in this language even if you type in English.",
    )
    language = normalize_language(language)

    if language != prev_lang:
        persist_farmer_language(user.get("farmer_id"), language)
        st.session_state.guide_language = language
        if role == "farmer" and st.session_state.get("guide_panel_open"):
            from src.ui.guide_chat import _welcome_message
            st.session_state.guide_messages = [
                {"role": "assistant", "content": _welcome_message(role, user, language)}
            ]
        st.toast(f"Answer language: {LANGUAGE_LABELS.get(language, language)}", icon="🗣️")

    if role == "farmer":
        status_bar(f"🗣️ {LANGUAGE_LABELS.get(language, language)}", sidebar=True)
    else:
        _render_staff_status(role)

    render_guide_sidebar_button(role, page_name, language)
    if role == "farmer":
        st.sidebar.caption(GUIDE_SHORT.replace("**", ""))

    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout", width="stretch"):
        logout_user()
        st.switch_page("pages/0_Login.py")

    return role, language


def render_main_alerts(role: str):
    if role != "farmer":
        return
    user = current_user() or {}
    farmer_id = user.get("farmer_id")
    if farmer_id:
        render_farmer_alerts(farmer_id)


def _render_staff_status(role: str):
    from src.resilience.network import is_online

    online = is_online()
    icon = "🟢" if online else "⚠️"
    label = "Online" if online else "Offline"

    if role == "admin":
        from src.resilience.llm_router import get_last_provider
        from src.rag.retriever import get_active_embedding_provider
        from src.integrations.tavily_search import tavily_available

        tav = "on" if tavily_available() else "off"
        status_bar(
            f"{icon} {label} · AI {get_last_provider()} · RAG {get_active_embedding_provider()} · Web {tav}",
            sidebar=True,
        )
    else:
        status_bar(f"{icon} {label}", sidebar=True)
