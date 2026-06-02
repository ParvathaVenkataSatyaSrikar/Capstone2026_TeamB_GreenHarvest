"""GreenHarvest — entry redirects to Login or role home."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

try:
    import truststore as ts
    ts.inject_into_ssl()
except ImportError:
    pass

from config.settings import _load_env_file
_load_env_file()

import streamlit as st
from src.ui.theme import bootstrap_app
from src.auth.session import init_auth_state, is_logged_in
from src.auth.rbac import ROLE_HOME
from src.auth.users import init_users

st.set_page_config(
    page_title="GreenHarvest Farmer Portal",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

bootstrap_app()
init_auth_state()
init_users()

if is_logged_in():
    st.switch_page(ROLE_HOME[st.session_state.auth_role])
else:
    st.switch_page("pages/0_Login.py")
