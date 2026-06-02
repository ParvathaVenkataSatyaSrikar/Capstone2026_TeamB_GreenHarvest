"""Login session state."""
import streamlit as st

from src.ui.brand import GH

ROLE_META = {
    "farmer": {"label": "Farmer", "icon": "🌾", "color": GH["farmer"]},
    "field_officer": {"label": "Field Officer", "icon": "👨‍🌾", "color": GH["officer"]},
    "admin": {"label": "Admin", "icon": "📊", "color": GH["admin"]},
}


def init_auth_state():
    defaults = {
        "auth_logged_in": False,
        "auth_user": None,
        "auth_role": None,
        "auth_redirect": None,
        "portal_language": "english",
        "guide_messages": [],
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def login_user(user: dict) -> None:
    """Store a plain dict so session survives Streamlit reruns."""
    safe = {
        "user_id": user.get("user_id"),
        "username": user.get("username"),
        "role": user.get("role"),
        "farmer_id": user.get("farmer_id"),
        "display_name": user.get("display_name"),
    }
    st.session_state.auth_logged_in = True
    st.session_state.auth_user = safe
    st.session_state.auth_role = safe["role"]
    st.session_state.portal_role = safe["role"]
    st.session_state.guide_messages = []
    st.session_state.chat_messages = []
    st.session_state._language_loaded = False
    lang = "english"
    if safe.get("farmer_id"):
        try:
            from src.integrations.profile import get_profile
            from src.i18n.language import normalize_language
            profile = get_profile(safe["farmer_id"]) or {}
            lang = normalize_language(profile.get("language"))
        except Exception:
            pass
    st.session_state.portal_language = lang


def logout_user() -> None:
    for key in (
        "auth_logged_in", "auth_user", "auth_role", "auth_redirect",
        "guide_messages", "chat_messages", "last_result", "active_farmer_id",
        "portal_role", "staff_authenticated", "staff_pwd_input", "_language_loaded",
        "guide_panel_open",
    ):
        if key in st.session_state:
            del st.session_state[key]


def is_logged_in() -> bool:
    init_auth_state()
    return bool(st.session_state.auth_logged_in and st.session_state.auth_user)


def current_user() -> dict | None:
    init_auth_state()
    return st.session_state.auth_user


def current_role() -> str | None:
    init_auth_state()
    return st.session_state.auth_role


def set_post_login_redirect(page_path: str) -> None:
    st.session_state.auth_redirect = page_path


def consume_post_login_redirect() -> str | None:
    path = st.session_state.get("auth_redirect")
    if path:
        st.session_state.auth_redirect = None
        return path
    return None


def require_login():
    if not is_logged_in():
        st.warning("Please log in to continue.")
        st.page_link("pages/0_Login.py", label="Go to Login")
        st.stop()


def require_permission(page_path: str):
    """Enforce login + RBAC for a page."""
    require_login()
    from src.auth.rbac import page_allowed, ROLE_HOME

    role = current_role()
    norm = page_path.replace("\\", "/")
    if not role or not page_allowed(role, norm):
        meta = ROLE_META.get(role, {})
        st.error(f"Access denied. This page is not part of the **{meta.get('label', role)}** portal.")
        if role in ROLE_HOME:
            st.page_link(ROLE_HOME[role], label=f"Go to {meta.get('label')} Home")
        st.stop()
