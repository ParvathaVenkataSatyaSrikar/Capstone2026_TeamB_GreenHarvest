"""Login — separate accounts per role (no role mixing)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from config.settings import _load_env_file
_load_env_file()

import streamlit as st
from src.ui.theme import bootstrap_app
from src.ui.components import apply_global_styles, auth_with_image, feature_chips
from src.auth.session import (
    init_auth_state, is_logged_in, login_user, set_post_login_redirect,
    consume_post_login_redirect,
)
from src.auth.users import authenticate, init_users
from src.auth.rbac import ROLE_HOME

st.set_page_config(
    page_title="Login | GreenHarvest",
    page_icon="🌾",
    layout="centered",
    initial_sidebar_state="expanded",
)
bootstrap_app()
apply_global_styles()
init_users()
init_auth_state()

redirect = consume_post_login_redirect()
if redirect:
    st.switch_page(redirect)

if is_logged_in():
    st.switch_page(ROLE_HOME[st.session_state.auth_role])

auth_with_image(
    "GreenHarvest",
    "Sign in to your portal — farmers, field officers, and admins each have their own space.",
)
feature_chips([
    ("🔐", "Secure login"),
    ("🌾", "Crop advisor"),
    ("👨‍🌾", "Expert review"),
    ("🌐", "6 languages"),
])

ROLE_OPTIONS = {
    "🌾 Farmer": {
        "role": "farmer",
        "blurb": "Farmer — AI crop advisor, saved chat history, expert review",
        "user_placeholder": "farmer_f001",
        "pass_placeholder": "farmer123",
        "button": "Sign in as Farmer",
    },
    "👨‍🌾 Field Officer": {
        "role": "field_officer",
        "blurb": "Field Officer — approve sensitive answers before farmers see them",
        "user_placeholder": "officer1",
        "pass_placeholder": "officer2026",
        "button": "Sign in as Field Officer",
    },
    "📊 Admin": {
        "role": "admin",
        "blurb": "Admin — analytics, governance, knowledge base",
        "user_placeholder": "admin",
        "pass_placeholder": "admin2026",
        "button": "Sign in as Admin",
    },
}


def _try_login(username: str, password: str, expected_role: str, label: str):
    user = authenticate(username, password, expected_role=expected_role)
    if user:
        login_user(user)
        set_post_login_redirect(ROLE_HOME[expected_role])
        st.rerun()
    st.error(f"Invalid {label} credentials. See demo accounts below.")


st.page_link("pages/00_Sign_Up.py", label="New farmer? Create account", icon="📝")
st.markdown("---")

portal = st.radio(
    "Portal",
    list(ROLE_OPTIONS.keys()),
    horizontal=True,
    label_visibility="collapsed",
    key="login_portal",
)
cfg = ROLE_OPTIONS[portal]
st.markdown(f"**{cfg['blurb']}**")

with st.form("login_form", clear_on_submit=False):
    username = st.text_input("Username", placeholder=cfg["user_placeholder"])
    password = st.text_input("Password", type="password", placeholder=cfg["pass_placeholder"])
    submitted = st.form_submit_button(cfg["button"], type="primary", width="stretch")

if submitted:
    _try_login(username, password, cfg["role"], cfg["role"].replace("_", " "))

with st.expander("Demo accounts", expanded=False):
    st.markdown("""
| Role | Username | Password |
|------|----------|----------|
| Farmer | `farmer_f001` … `farmer_f025` | `farmer123` |
| Field Officer | `officer1` … `officer5` | `officer2026` |
| Admin | `admin` | `admin2026` |

Examples: `farmer_f003` (Nashik tomato), `farmer_f018` (Vijayawada paddy), `officer2` (Priya Sharma).

After login you stay in **one portal** until **Logout**.

To refresh demo data: `python scripts/seed_demo_accounts.py`
""")
