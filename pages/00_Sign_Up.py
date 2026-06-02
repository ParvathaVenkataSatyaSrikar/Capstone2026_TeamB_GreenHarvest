"""Sign up — new farmer accounts with onboarding AI chatbot."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from config.settings import _load_env_file
_load_env_file()

import streamlit as st
from src.ui.theme import bootstrap_app
from src.ui.components import apply_global_styles
from src.auth.session import init_auth_state, is_logged_in, login_user, set_post_login_redirect
from src.auth.users import register_farmer, init_users, username_available
from src.auth.rbac import ROLE_HOME
from src.onboarding.assistant import ask_onboarding

st.set_page_config(
    page_title="Sign Up | GreenHarvest",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded",
)
bootstrap_app()
apply_global_styles()
init_users()
init_auth_state()

if is_logged_in():
    st.switch_page(ROLE_HOME[st.session_state.auth_role])

st.markdown(
    """
    <div style="text-align:center;padding:1rem 0;">
        <h1 style="color:#14532d;margin:0;">Join GreenHarvest</h1>
        <p style="color:#64748b;">Create your farmer account — AI crop support in your language</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if "onboard_messages" not in st.session_state:
    st.session_state.onboard_messages = [
        {"role": "assistant", "content": "Hi! I'm your sign-up guide. Ask me about username, password, crop, or how GreenHarvest works."}
    ]

col_form, col_bot = st.columns([1.1, 1])

with col_form:
    st.markdown("### Create farmer account")
    with st.form("signup_form"):
        display_name = st.text_input("Full name", placeholder="Ramesh Kumar")
        username = st.text_input("Username", placeholder="farmer_ramesh")
        password = st.text_input("Password", type="password", placeholder="Min 6 characters")
        password2 = st.text_input("Confirm password", type="password")
        district = st.text_input("District", placeholder="Warangal")
        from src.rag.crop_catalog import CROP_NAMES
        crop_opts = sorted({c for c in CROP_NAMES if c not in ("rice", "corn", "peanut", "chili", "eggplant")})
        crop = st.selectbox("Main crop", crop_opts, index=crop_opts.index("cotton") if "cotton" in crop_opts else 0)
        land_acres = st.number_input("Land (acres)", min_value=0.1, value=2.0, step=0.1)
        irrigation = st.selectbox("Irrigation", ["drip", "canal", "rainfed", "sprinkler"])
        state_name = st.text_input("State (optional)", placeholder="Telangana")
        phone = st.text_input("Phone (optional)", placeholder="9876543210")
        language = st.selectbox("Preferred language", ["english", "hindi", "telugu", "tamil", "marathi", "punjabi"])
        own_data = st.checkbox(
            "I confirm this is my own information (demo app — not linked to government farmer databases)",
            value=False,
        )

        submitted = st.form_submit_button("Create account", type="primary", width="stretch")

    st.caption(
        "Your name, district, crop, and phone are stored locally for this demo. "
        "We do not import Aadhaar or government registry data."
    )

    if submitted:
        if not own_data:
            st.error("Please confirm that you are entering your own information.")
        elif password != password2:
            st.error("Passwords do not match.")
        elif not username_available(username):
            st.error("Username invalid or already taken.")
        else:
            user, err = register_farmer(
                username, password, display_name, district, crop, phone, language,
                land_acres=land_acres, irrigation_type=irrigation,
            )
            if user:
                login_user(user)
                set_post_login_redirect(ROLE_HOME["farmer"])
                st.success(f"Welcome, {user['display_name']}! Farmer ID: {user['farmer_id']}")
                st.rerun()
            else:
                st.error(err or "Registration failed.")

    st.page_link("pages/0_Login.py", label="Already have an account? Sign in")
    st.caption("Officer and admin accounts are created by your organization administrator.")

with col_bot:
    st.markdown("### Sign-up assistant")
    st.caption("Ask about usernames, passwords, crops, or how GreenHarvest works.")

    for msg in st.session_state.onboard_messages[-8:]:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    q = st.chat_input("Ask about sign-up…", key="onboard_input")
    if q:
        st.session_state.onboard_messages.append({"role": "user", "content": q})
        answer = ask_onboarding(q, st.session_state.onboard_messages[:-1])
        st.session_state.onboard_messages.append({"role": "assistant", "content": answer})
        st.rerun()
