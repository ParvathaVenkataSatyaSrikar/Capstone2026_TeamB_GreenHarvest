"""Multilingual support — preferred language for all farmer-facing AI text."""
from __future__ import annotations

import hashlib
import streamlit as st

SUPPORTED_LANGUAGES = ["english", "hindi", "telugu", "tamil", "marathi", "punjabi"]

LANGUAGE_LABELS = {
    "english": "English",
    "hindi": "हिन्दी (Hindi)",
    "telugu": "తెలుగు (Telugu)",
    "tamil": "தமிழ் (Tamil)",
    "marathi": "मराठी (Marathi)",
    "punjabi": "ਪੰਜਾਬੀ (Punjabi)",
}

# Full names for LLM prompts
LANGUAGE_PROMPT_NAMES = {
    "english": "English",
    "hindi": "Hindi (Devanagari script)",
    "telugu": "Telugu (Telugu script)",
    "tamil": "Tamil (Tamil script)",
    "marathi": "Marathi (Devanagari script)",
    "punjabi": "Punjabi (Gurmukhi script)",
}

PENDING_FARMER_MSG = {
    "english": (
        "Thank you. Your question has been sent to a GreenHarvest agriculture expert. "
        "You will see the full approved guidance in **My Queries** soon."
    ),
    "hindi": (
        "धन्यवाद। आपका प्रश्न ग्रीनहार्वेस्ट कृषि विशेषज्ञ के पास भेज दिया गया है। "
        "स्वीकृत सलाह जल्द ही **मेरे प्रश्न** में दिखेगी।"
    ),
    "telugu": (
        "ధన్యవాదాలు. మీ ప్రశ్న గ్రీన్‌హార్వెస్ట్ వ్యవసాయ నిపుణులకు పంపబడింది. "
        "ఆమోదించిన సలహా త్వరలో **నా ప్రశ్నలు**లో కనిపిస్తుంది."
    ),
    "tamil": (
        "நன்றி. உங்கள் கேள்வி கிரீன்ஹார்வெஸ்ட் விவசாய நிபுணரிடம் அனுப்பப்பட்டது. "
        "அங்கீகரிக்கப்பட்ட ஆலோசனை விரைவில் **என் கேள்விகள்** பகுதியில் தெரியும்."
    ),
    "marathi": (
        "धन्यवाद. तुमचा प्रश्न ग्रीनहार्वेस्ट कृषी तज्ज्ञाकडे पाठवला आहे. "
        "मंजूर सल्ला लवकरच **माझे प्रश्न** मध्ये दिसेल."
    ),
    "punjabi": (
        "ਧੰਨਵਾਦ। ਤੁਹਾਡਾ ਸਵਾਲ ਗ੍ਰੀਨਹਾਰਵੇਸਟ ਕਿਸਾਨ ਮਾਹਿਰ ਨੂੰ ਭੇਜ ਦਿੱਤਾ ਗਿਆ ਹੈ। "
        "ਮਨਜ਼ੂਰ ਸਲਾਹ ਜਲਦੀ **ਮੇਰੇ ਸਵਾਲ** ਵਿੱਚ ਦਿਖੇਗੀ।"
    ),
}


def normalize_language(lang: str | None) -> str:
    if not lang:
        return "english"
    key = lang.strip().lower()
    return key if key in SUPPORTED_LANGUAGES else "english"


def is_english(lang: str | None) -> bool:
    return normalize_language(lang) == "english"


def get_session_language() -> str:
    st_any = st.session_state
    return normalize_language(st_any.get("portal_language", "english"))


def language_directive(lang: str | None) -> str:
    """Instruction block for LLM — answer in preferred language even if query is English."""
    code = normalize_language(lang)
    if is_english(code):
        return (
            "Write your entire response in clear, simple English for farmers."
        )
    name = LANGUAGE_PROMPT_NAMES.get(code, code)
    return (
        f"FARMER PREFERRED LANGUAGE: {name}.\n"
        f"You MUST write the ENTIRE recommendation, safety notes, and steps in {name} only.\n"
        "The farmer may type their question in English — still answer in the preferred language.\n"
        "Use simple words. Keep crop and scheme names accurate. Use the correct script for that language."
    )


def pending_message(lang: str | None) -> str:
    code = normalize_language(lang)
    return PENDING_FARMER_MSG.get(code, PENDING_FARMER_MSG["english"])


def _translation_cache_key(text: str, lang: str) -> str:
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
    return f"{normalize_language(lang)}:{digest}"


def _get_translation_cache() -> dict[str, str]:
    if "gh_translation_cache" not in st.session_state:
        st.session_state.gh_translation_cache = {}
    return st.session_state.gh_translation_cache


def translate_text(text: str, lang: str | None) -> str:
    """Translate farmer-visible text to preferred language (cached per session)."""
    if not text or not text.strip():
        return text
    code = normalize_language(lang)
    if is_english(code):
        return text

    cache = _get_translation_cache()
    key = _translation_cache_key(text, code)
    if key in cache:
        return cache[key]

    from langchain_core.messages import HumanMessage, SystemMessage
    from src.resilience.llm_router import invoke_messages

    target = LANGUAGE_PROMPT_NAMES.get(code, code)
    # Trim very long FAQ blocks — LLM translates faster; full guide uses dedicated LLM path
    source = text if len(text) <= 2400 else text[:2400] + "\n\n…"
    try:
        result = invoke_messages([
            SystemMessage(
                content=(
                    f"You are a professional translator for Indian farmers. "
                    f"Translate the following app-help message into {target}. "
                    "Preserve markdown, bullets, and app names (AI Crop Advisor, My Queries). "
                    "Output ONLY the translation."
                )
            ),
            HumanMessage(content=source),
        ])
        out = (result.content or "").strip()
        if len(out) > 20:
            cache[key] = out
            return out
    except Exception:
        pass
    return text


def apply_guide_language(text: str, lang: str | None) -> str:
    """Translate Portal Assistant text when not English (cached)."""
    if not text or is_english(lang):
        return text
    non_latin = sum(1 for c in text if ord(c) > 127)
    if non_latin >= max(12, len(text) * 0.12):
        return text
    if len(text) > 2800:
        return text
    return translate_text(text, lang)


def apply_farmer_language(text: str, lang: str | None, *, allow_translate: bool = True) -> str:
    """Ensure text is in farmer's preferred language (translate if model replied in English)."""
    if not text or is_english(lang) or not allow_translate:
        return text
    non_latin = sum(1 for c in text if ord(c) > 127)
    if non_latin >= max(12, len(text) * 0.12):
        return text
    from src.resilience.llm_router import get_last_provider
    if get_last_provider() == "offline":
        return text
    return translate_text(text, lang)


def persist_farmer_language(farmer_id: str | None, lang: str) -> None:
    """Save preferred language to farmer profile when changed in sidebar."""
    if not farmer_id:
        return
    from src.integrations.profile import get_profile, save_profile

    profile = get_profile(farmer_id)
    if not profile:
        return
    code = normalize_language(lang)
    if profile.get("language") != code:
        save_profile({**profile, "language": code})
