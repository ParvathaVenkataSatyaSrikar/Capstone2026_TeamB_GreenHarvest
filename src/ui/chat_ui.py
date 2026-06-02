"""Farmer AI chat experience — clean, user-facing (no backend jargon)."""

from __future__ import annotations

import streamlit as st

from src.ui.components import render_response_box, render_chat_message
from src.ui.farmer_copy import render_review_status, friendly_intent, explain_escalation_reason
from src.ui.roles import FARMER_QUICK_QUESTIONS
from src.ui.chat_history import load_chat_from_db
from src.i18n.language import get_session_language





def init_chat_state(farmer_id: str, reload_history: bool = False):
    prev = st.session_state.get("active_farmer_id")
    if prev != farmer_id or reload_history or "chat_messages" not in st.session_state:
        st.session_state.chat_messages = load_chat_from_db(farmer_id, language=get_session_language())
        st.session_state.last_result = None
    if "last_result" not in st.session_state:
        st.session_state.last_result = None
    st.session_state.active_farmer_id = farmer_id





def render_quick_questions() -> str | None:
    st.markdown('<p class="gh-quick-label">Suggested questions</p>', unsafe_allow_html=True)
    selected = None
    cols = st.columns(2)
    for i, q in enumerate(FARMER_QUICK_QUESTIONS):
        with cols[i % 2]:
            if st.button(q, key=f"quick_{i}", width="stretch"):
                selected = q
    return selected





def _set_pending_image(data: bytes, mime: str) -> None:
    st.session_state.chat_pending_image = {"bytes": data, "mime": mime}


def _clear_pending_image() -> None:
    st.session_state.pop("chat_pending_image", None)
    st.session_state.pop("_chat_upload_key", None)


def _bump_upload_widget() -> None:
    """New uploader key so Streamlit clears the file widget after send/remove."""
    st.session_state.chat_upload_nonce = st.session_state.get("chat_upload_nonce", 0) + 1


def _apply_uploaded_file(uploaded) -> None:
    if uploaded is None:
        return
    # getvalue() is safe across reruns; read() can return empty bytes on 2nd call
    data = uploaded.getvalue() if hasattr(uploaded, "getvalue") else uploaded.read()
    if not data:
        return
    mime = uploaded.type or "image/jpeg"
    blob_key = (uploaded.name, uploaded.size, len(data))
    st.session_state["_chat_upload_key"] = blob_key
    _set_pending_image(data, mime)


def render_chat_image_attach() -> dict | None:
    """Attach crop photo in-chat via Streamlit file uploader (drag-and-drop + browse)."""
    upload_key = f"chat_crop_upload_{st.session_state.get('chat_upload_nonce', 0)}"
    uploaded = st.file_uploader(
        "📷 Attach crop photo (drag & drop here, or click Browse)",
        type=["jpg", "jpeg", "png", "webp"],
        key=upload_key,
        help=(
            "Drag an image onto this box, or click Browse. "
            "After a screenshot (Win+Shift+S / Mac screenshot), drag the saved image here."
        ),
    )
    if uploaded is not None:
        data = uploaded.getvalue() if hasattr(uploaded, "getvalue") else uploaded.read()
        blob_key = (uploaded.name, uploaded.size, len(data))
        pending = st.session_state.get("chat_pending_image")
        # Re-attach when user uploads again, or widget still has a file but pending was cleared
        if st.session_state.get("_chat_upload_key") != blob_key or not pending:
            _apply_uploaded_file(uploaded)

    pending = st.session_state.get("chat_pending_image")
    if pending:
        prev_col, btn_col = st.columns([4, 1])
        with prev_col:
            st.image(pending["bytes"], caption="Attached crop photo", width=220)
        with btn_col:
            if st.button("✕ Remove", key="chat_remove_image", width="stretch"):
                _clear_pending_image()
                _bump_upload_widget()
                st.rerun()
    return pending


def process_image_message(
    profile: dict,
    image: dict,
    language: str,
    role: str,
    farmer_note: str = "",
) -> None:
    farmer_id = profile["farmer_id"]
    note = (farmer_note or "").strip() or "Crop photo for diagnosis"
    init_chat_state(farmer_id)

    st.session_state.chat_messages.append({
        "role": "user",
        "text": f"📷 {note}",
        "image_bytes": image["bytes"],
        "image_mime": image.get("mime", "image/jpeg"),
    })

    with st.spinner("Analyzing your crop photo…"):
        from src.services.support_service import run_image_diagnosis

        try:
            result = run_image_diagnosis(
                farmer_id=farmer_id,
                image_bytes=image["bytes"],
                mime=image.get("mime", "image/jpeg"),
                crop=profile.get("crop", ""),
                district=profile.get("district", ""),
                farmer_note=note,
                language=language,
                user_role=role,
            )
        except Exception:
            st.error("Could not analyze the image. Try another photo or describe symptoms in text.")
            return

    _clear_pending_image()
    _bump_upload_widget()
    st.session_state.last_result = result
    st.session_state.chat_messages.append({
        "role": "assistant",
        "text": result.translated_response,
        "meta": {
            "review_status": result.review_status,
            "escalation_reason": result.escalation_reason,
            "vision": True,
        },
    })


def process_query(profile: dict, query: str, language: str, role: str) -> None:
    farmer_id = profile["farmer_id"]
    query = (query or "").strip()
    if not query:
        st.warning("Please type a question or pick a quick question below.")
        return

    init_chat_state(farmer_id)
    st.session_state.chat_messages.append({"role": "user", "text": query})

    with st.spinner("Finding the best advice for you…"):
        from src.services.support_service import run_support_query

        try:
            result = run_support_query(
                farmer_id=farmer_id,
                query=query,
                user_role=role,
                language=language,
            )
        except Exception:
            st.error(
                "Something went wrong. Your question was noted — "
                "please try again or use **My Queries** later."
            )
            return

    st.session_state.last_result = result
    if result.agent_trace.get("fallback"):
        st.toast("Answer from saved crop guides", icon="📚")

    response_text = result.translated_response

    st.session_state.chat_messages.append({

        "role": "assistant",

        "text": response_text,

        "meta": {

            "review_status": result.review_status,

            "escalation_reason": result.escalation_reason,

        },

    })





def render_chat_history():
    msgs = st.session_state.get("chat_messages", [])
    if not msgs:
        st.markdown(
            '<div class="gh-empty-chat">'
            '<div class="icon">🌱</div>'
            '<p class="title">Ask your crop advisor</p>'
            '<p>Type a question below, tap a suggestion, or attach a leaf photo.</p>'
            '<p>We remember your farm profile and save every conversation.</p>'
            '</div>',
            unsafe_allow_html=True,
        )
        return
    for msg in msgs:
        meta = msg.get("meta") or {}
        status = meta.get("review_status") if msg["role"] == "assistant" else None
        if msg.get("image_bytes"):
            st.image(msg["image_bytes"], width=200)
        render_chat_message(msg["text"], is_user=(msg["role"] == "user"), review_status=status)





def render_last_result_details():

    result = st.session_state.get("last_result")

    if not result:

        return



    st.markdown("---")
    st.markdown(
        '<p class="gh-quick-label" style="margin-top:0.5rem;">What happens next</p>',
        unsafe_allow_html=True,
    )

    render_review_status(

        result.review_status,

        escalation_reason=result.escalation_reason or "",

        confidence=result.final_confidence if result.review_status == "auto_approved" else None,

    )



    if result.review_status == "pending_human":

        st.info(

            "Your question is with a **GreenHarvest field officer**. "

            "You will see the full answer in **My Queries** once it is approved. "

            f"{explain_escalation_reason(result.escalation_reason or '')}"

        )

        if result.draft_response:

            with st.expander("Preview while you wait", expanded=False):

                st.caption("This may change after expert review.")

                preview = result.draft_response

                if len(preview) > 800:

                    preview = preview[:800] + "…"

                render_response_box(preview)

    elif result.review_status == "auto_approved":

        topic = friendly_intent(result.intent)

        st.caption(f"Topic: **{topic}** · Based on trusted crop guides and your farm profile.")





def render_chat_toolbar(farmer_id: str):
    st.markdown('<div class="gh-chat-toolbar">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1, 2])
    with c1:
        if st.button("↻ Refresh", width="stretch"):
            st.session_state.chat_messages = load_chat_from_db(farmer_id, language=get_session_language())
            st.session_state.last_result = None
            st.rerun()
    with c2:
        if st.button("Clear screen", width="stretch"):
            st.session_state.chat_messages = []
            st.session_state.last_result = None
            st.rerun()
    with c3:
        st.caption("Saved automatically · Expert-reviewed answers appear in **My Queries**")
    st.markdown("</div>", unsafe_allow_html=True)

