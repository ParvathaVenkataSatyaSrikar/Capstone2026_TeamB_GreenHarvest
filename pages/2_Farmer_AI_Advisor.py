"""Farmer portal — AI Crop Advisor chat."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import streamlit as st
from src.ui.theme import bootstrap_app
from src.ui.components import (
    apply_global_styles, page_header, section_card, end_card,
    chat_panel_start, chat_panel_end, profile_strip, section_title,
)
from src.ui.system_status import render_health_banner
from src.ui.portal import render_role_sidebar, render_main_alerts
from src.auth.session import require_permission, current_user
from src.ui.chat_ui import (
    init_chat_state, render_quick_questions, process_query, process_image_message,
    render_chat_history, render_last_result_details, render_chat_toolbar,
    render_chat_image_attach,
)
from src.integrations.profile import list_profiles, save_profile
from src.i18n.language import LANGUAGE_LABELS, normalize_language

bootstrap_app()
apply_global_styles()
require_permission("pages/2_Farmer_AI_Advisor.py")
role, language = render_role_sidebar("AI Crop Advisor")
render_main_alerts(role)
render_health_banner(role)

user = current_user()
farmer_id = user.get("farmer_id")
if not farmer_id:
    st.error("Your account is not linked to a farmer profile. Use farmer_f001 or farmer_f002 to log in.")
    st.stop()

page_header(
    "AI Crop Advisor",
    "Personalized farming guidance in your language — with expert backup when you need it",
    role=role,
    image_key="wheat",
)

profiles = [p for p in list_profiles() if p["farmer_id"] == farmer_id]
if not profiles:
    st.error("No farm profile linked to your account. Contact support.")
    st.stop()
profile = profiles[0]
lang_label = LANGUAGE_LABELS.get(normalize_language(language), language)

profile_strip(
    profile["name"],
    profile.get("crop", "crop"),
    profile.get("district", ""),
    lang_label,
)

init_chat_state(profile["farmer_id"])

_open = st.session_state.pop("farmer_open_tab", None)
if _open == "schemes":
    st.info("Open the **Schemes** tab below for eligible programs and demo payment status.")
elif _open == "dealers":
    st.info("Open the **Dealers** tab below for the demo dealer directory.")

tab_chat, tab_profile, tab_schemes, tab_insights, tab_dealers = st.tabs(
    ["Chat", "My farm", "Schemes", "Insights", "Dealers"]
)

with tab_profile:
    from src.integrations.weather import get_weather
    from src.integrations.soil import get_soil_report
    from src.rag.crop_catalog import CROP_NAMES
    from src.advisory.crop_lifecycle import LIFECYCLE_STAGES
    from src.ui.farmer_insights import render_weather_alert_banner, render_lifecycle_card

    c1, c2 = st.columns(2, gap="large")
    with c1:
        section_card("Farm profile")
        crops = sorted(set(CROP_NAMES) - {"rice", "corn", "peanut", "chili", "eggplant"})
        cur = profile.get("crop", "cotton")
        new_crop = st.selectbox("Main crop", crops, index=crops.index(cur) if cur in crops else 0)
        district = st.text_input("District", profile.get("district", ""))
        land_acres = st.number_input(
            "Land (acres)", min_value=0.1, max_value=500.0,
            value=float(profile.get("land_acres") or 2.0), step=0.1,
        )
        stages = list(LIFECYCLE_STAGES)
        cur_stage = profile.get("crop_stage", "vegetative")
        from src.advisory.crop_lifecycle import normalize_stage
        cur_stage = normalize_stage(cur_stage)
        stage = st.selectbox(
            "Growth stage",
            stages,
            index=stages.index(cur_stage) if cur_stage in stages else 2,
        )
        irrigation = st.selectbox(
            "Irrigation",
            ["drip", "canal", "rainfed", "sprinkler"],
            index=["drip", "canal", "rainfed", "sprinkler"].index(
                profile.get("irrigation_type", "drip")
            ) if profile.get("irrigation_type") in ("drip", "canal", "rainfed", "sprinkler") else 0,
        )
        if st.button("Save profile", type="primary", width="stretch"):
            save_profile({
                **profile, "crop": new_crop, "district": district,
                "crop_stage": stage, "land_acres": land_acres, "irrigation_type": irrigation,
            })
            st.success("Profile updated — your next answers will use these details.")
            st.rerun()
        end_card()
    with c2:
        section_card("Weather & soil", image_key="irrigation")
        render_weather_alert_banner(profile)
        w = get_weather(profile["district"], profile["crop"])
        st.caption(w.get("forecast_3day", ""))
        s = get_soil_report(profile["farmer_id"], profile["district"], profile["crop"])
        st.metric("Soil pH", s.get("ph", "—"))
        st.caption(s.get("recommendation", "")[:220])
        render_lifecycle_card(profile)
        end_card()

with tab_schemes:
    from src.ui.farmer_insights import render_scheme_cards
    from src.ui.farmer_services import render_scheme_payment_tab

    section_card("Recommended schemes")
    st.caption("Matched to your crop, district, and land size.")
    render_scheme_cards(profile)
    end_card()
    section_card("Payment status (demo)")
    render_scheme_payment_tab(profile["farmer_id"], profile.get("district", ""))
    end_card()

with tab_insights:
    from src.ui.farmer_insights import render_sustainability_panel

    section_card("Farm insights")
    render_sustainability_panel(profile)
    end_card()

with tab_dealers:
    from src.ui.farmer_services import render_dealer_tab

    section_card("Dealers & callback")
    render_dealer_tab(profile["farmer_id"], profile)
    end_card()

with tab_chat:
    left, right = st.columns([2.2, 1], gap="large")

    with right:
        section_card("Tips for better answers", image_key="farmer")
        st.markdown("""
**Be specific**  
Crop + symptom + district in one message.

**Photo diagnosis**  
Attach a clear leaf photo, then press Enter.

**Fast topics**  
Irrigation, fertilizer, mandi price, schemes.

**Expert review**  
Pests, insurance, and urgent issues go to a field officer.

**App help**  
Use **Portal Assistant** in the sidebar.
        """)
        end_card()
        if st.button("View all my queries", type="secondary", width="stretch"):
            st.switch_page("pages/3_Farmer_My_Queries.py")

    with left:
        section_card("Conversation")
        chat_panel_start()
        render_chat_toolbar(profile["farmer_id"])
        render_chat_history()
        quick = render_quick_questions()

        st.markdown('<p class="gh-quick-label">Attach crop photo</p>', unsafe_allow_html=True)
        pending_image = render_chat_image_attach()

        with st.expander("Voice question (optional)", expanded=False):
            from src.integrations.voice import transcribe_audio_bytes

            st.caption("Record a short question — we convert it to text and send it like a typed message.")
            audio = st.audio_input("Record", key="crop_advisor_voice")
            if audio is not None:
                blob = audio.getvalue() if hasattr(audio, "getvalue") else audio.read()
                blob_key = hash(blob)
                if st.session_state.get("_voice_blob_key") != blob_key:
                    st.session_state["_voice_blob_key"] = blob_key
                    vt, ve = transcribe_audio_bytes(blob, language)
                    st.session_state["_voice_text"] = vt
                    st.session_state["_voice_err"] = ve
                voice_text = st.session_state.get("_voice_text")
                voice_err = st.session_state.get("_voice_err")
                if voice_text:
                    st.success(f'Heard: "{voice_text}"')
                    if st.button("Send voice question", type="primary", key="send_voice"):
                        st.session_state["_voice_pending_query"] = voice_text
                        st.rerun()
                elif voice_err:
                    st.warning(voice_err)

        query = st.chat_input("Type your question here…")
        if quick:
            query = quick
        pending_voice = st.session_state.pop("_voice_pending_query", None)
        if pending_voice:
            query = pending_voice

        submitted = query is not None
        if submitted:
            pending_image = st.session_state.get("chat_pending_image") or pending_image
            text = (query or "").strip()
            if pending_image:
                process_image_message(profile, pending_image, language, role, farmer_note=text)
                st.rerun()
            elif text:
                process_query(profile, text, language, role)
                st.rerun()
            else:
                st.warning("Type a question or attach a photo.")
        elif pending_image and st.button("Analyze photo", type="primary", key="analyze_photo_btn", width="stretch"):
            process_image_message(profile, pending_image, language, role)
            st.rerun()

        chat_panel_end()
        end_card()
        render_last_result_details()
