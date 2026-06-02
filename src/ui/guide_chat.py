"""Portal Assistant — sidebar help panel."""
import streamlit as st

from src.ui.branding import GUIDE_NAME, GUIDE_TAGLINE
from src.auth.session import current_user
from src.db.repository import get_farmer_kpis
from src.i18n.guide_strings import (
    localized_farmer_welcome,
    localized_farmer_welcome_simple,
    GUIDE_LANG_HINT,
)
from src.i18n.language import normalize_language, is_english


def _ensure_guide_state():
    if "guide_messages" not in st.session_state:
        st.session_state.guide_messages = []


def _welcome_message(role: str, user: dict | None = None, language: str = "english") -> str:
    """Instant welcome — no API call (fixes freeze on language change)."""
    lang = normalize_language(language)
    user = user or {}

    if role == "farmer":
        fid = user.get("farmer_id")
        if fid:
            fk = get_farmer_kpis(fid)
            text = localized_farmer_welcome(fk["total_queries"], fk["pending_review"], lang)
        else:
            text = localized_farmer_welcome_simple(lang)
    elif role == "field_officer":
        from src.helper.live_context import officer_welcome
        text = officer_welcome(user)
        if not is_english(lang):
            from src.i18n.language import apply_guide_language
            text = apply_guide_language(text, lang)
    else:
        from src.db.repository import get_kpis
        kpis = get_kpis()
        text = (
            f"Welcome to **{GUIDE_NAME}**.\n\n"
            f"**Live:** {kpis['pending_hitl']} pending HITL · {kpis['open_escalations']} open cases · "
            f"{kpis['queries_today']} queries today.\n\n"
            "Ask: *System overview* · *Where is Knowledge Base?*"
        )
        if not is_english(lang):
            from src.i18n.language import apply_guide_language
            text = apply_guide_language(text, lang)

    hint = GUIDE_LANG_HINT.get(lang, "")
    if hint:
        text += f"\n\n*{hint}*"
    return text


@st.fragment
def _guide_chat_panel(role: str, page_name: str, language: str, user: dict):
    """Isolated reruns — language changes outside fragment won't block the whole app."""
    _ensure_guide_state()
    lang = normalize_language(language)

    prev_lang = st.session_state.get("guide_language")
    if prev_lang != lang:
        st.session_state.guide_language = lang
        st.session_state.guide_messages = [
            {"role": "assistant", "content": _welcome_message(role, user, lang)}
        ]
    elif not st.session_state.guide_messages:
        st.session_state.guide_messages = [
            {"role": "assistant", "content": _welcome_message(role, user, lang)}
        ]

    quick = {
        "farmer": [
            "How long until expert answers?",
            "How do I use this app?",
            "How many are waiting for expert?",
        ],
        "field_officer": [
            "How many reviews should I do?",
            "What's in my queue?",
            "How do I approve a query?",
        ],
        "admin": [
            "System overview",
            "Where is Knowledge Base?",
            "Pending HITL count",
        ],
    }.get(role, ["How does this app work?"])

    qcols = st.columns(3)
    for i, label in enumerate(quick[:3]):
        with qcols[i]:
            if st.button(label, key=f"guide_quick_{role}_{i}", width="stretch"):
                _append_guide_exchange(role, page_name, label, lang, user)

    prompt = st.chat_input(f"Ask {GUIDE_NAME}…", key=f"guide_input_{role}")
    if prompt:
        _append_guide_exchange(role, page_name, prompt, lang, user)

    # Render after handling input — otherwise answers appear one question late
    for msg in st.session_state.guide_messages[-6:]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Clear", key=f"guide_clear_{role}", width="stretch"):
            st.session_state.guide_messages = [
                {"role": "assistant", "content": _welcome_message(role, user, lang)}
            ]
    with c2:
        if st.button("Close", key=f"guide_close_{role}", width="stretch"):
            st.session_state.guide_panel_open = False


def _append_guide_exchange(role: str, page_name: str, text: str, language: str, user: dict):
    from src.helper.assistant import ask_guide

    _ensure_guide_state()
    st.session_state.guide_messages.append({"role": "user", "content": text})
    history = st.session_state.guide_messages[:-1]
    with st.spinner("One moment…"):
        answer = ask_guide(role, text, page_name, history, language=language, user=user)
    st.session_state.guide_messages.append({"role": "assistant", "content": answer})


def render_guide_sidebar_button(role: str, page_name: str = "", language: str = "english"):
    if "guide_panel_open" not in st.session_state:
        st.session_state.guide_panel_open = False

    st.sidebar.markdown(f"##### 📖 {GUIDE_NAME}")
    st.sidebar.caption("Live counts · navigation · review timing")

    if st.sidebar.button(
        f"Open {GUIDE_NAME}",
        width="stretch",
        help="App help — not crop advice",
        key=f"open_guide_{role}",
    ):
        st.session_state.guide_panel_open = True

    if st.session_state.guide_panel_open:
        user = current_user() or {}
        with st.sidebar.container(border=True):
            st.markdown(f"**{GUIDE_NAME}**")
            st.caption(GUIDE_TAGLINE)
            _guide_chat_panel(role, page_name, language, user)
