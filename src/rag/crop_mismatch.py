"""When farmer asks about a crop other than their profile crop."""
from __future__ import annotations

from src.rag.crop_catalog import normalize_crop


def get_effective_query_crop(profile_crop: str, query: str, entities: dict) -> tuple[str, str | None]:
    """
    Returns (crop_for_rag, query_crop_if_different).
    RAG uses the crop the farmer is asking about; profile crop kept for notice.
    """
    profile = normalize_crop(profile_crop or "")
    from_entities = normalize_crop(entities.get("crop") or "")
    from_query = None
    from src.rag.crop_catalog import detect_crop_in_text
    detected = detect_crop_in_text(query)
    if detected:
        from_query = detected

    query_crop = from_query or from_entities or profile
    if query_crop and profile and query_crop != profile:
        return query_crop, query_crop
    return query_crop or profile, None


def build_crop_mismatch_notice(profile_crop: str, query_crop: str, language: str = "english") -> str:
    pc = (profile_crop or "your registered crop").title()
    qc = (query_crop or "").title()
    notices = {
        "english": (
            f"**Note:** Your farm profile crop is **{pc}**, but you asked about **{qc}**. "
            f"The guidance below is for **{qc}** — update your profile in **My farm** if you have switched crops."
        ),
        "hindi": (
            f"**नोट:** आपकी प्रोफ़ाइल फसल **{pc}** है, लेकिन आपने **{qc}** के बारे में पूछा है। "
            f"नीचे की सलाह **{qc}** के लिए है।"
        ),
        "telugu": (
            f"**గమనిక:** మీ ప్రొఫైల్ పంట **{pc}**, కానీ మీరు **{qc}** గురించి అడిగారు. "
            f"క్రింది సలహ **{qc}** కోసం."
        ),
    }
    lang = (language or "english").lower()
    return notices.get(lang, notices["english"])
