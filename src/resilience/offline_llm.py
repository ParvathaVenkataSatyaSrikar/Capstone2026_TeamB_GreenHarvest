"""Offline LLM — grounded answers from local KB + rules (no API)."""
import json
import re

from src.rag.retriever import retrieve


def _extract_user_query(system: str, user: str) -> str:
    for line in user.splitlines():
        if line.strip().lower().startswith("query:"):
            return line.split(":", 1)[1].strip()
    return user.strip()[:500]


def _parse_role_from_system(system: str) -> str:
    m = re.search(r"Current user role:\s*(\w+)", system, re.I)
    if m:
        return m.group(1).lower()
    return "farmer"


def _is_app_guide_request(system: str) -> bool:
    s = system.lower()
    return any(
        marker in s
        for marker in (
            "your friend",
            "krishi guide",
            "live app data",
            "application knowledge",
            "you are your friend",
            "you are krishi guide",
            "app coach for greenharvest",
        )
    )


def _guide_offline(system: str, user: str) -> str:
    """App help assistant must never return crop RAG — app help only."""
    from src.helper.knowledge_base import match_faq, offline_guide_answer

    query = _extract_user_query(system, user)
    role = _parse_role_from_system(system)
    q = query.lower()

    broad = any(
        p in q
        for p in (
            "how to use", "use the app", "use this app", "how do i use",
            "get started", "tutorial", "walk me through", "how does this work",
        )
    )
    if broad:
        return offline_guide_answer(role, query, force_full=True)

    hit = match_faq(query, role)
    if hit:
        return hit

    return offline_guide_answer(role, query)


def offline_compose(system: str, user: str) -> str:
    """Build a helpful offline response using keyword RAG + templates."""
    query = _extract_user_query(system, user)
    lower = query.lower()
    crop_hint = _parse_crop_from_user(user)

    # Application help (Portal Assistant) FIRST — before crop/recommendation paths
    if _is_app_guide_request(system):
        return _guide_offline(system, user)

    if "sign up" in system.lower() or "registration" in system.lower() or "onboarding" in system.lower():
        return _onboarding_offline(user)

    if "json" in system.lower() and "recommendation" in system.lower():
        return _crop_offline_json(query, lower, crop_hint)

    if "helper" in system.lower() or "your friend" in system.lower() or "krishi guide" in system.lower():
        return _guide_offline(system, user)

    return _crop_offline_text(query, lower, crop_hint)


def _onboarding_offline(user: str) -> str:
    u = user.lower()
    if "password" in u:
        return "Choose a password with at least 6 characters. You will use it every time you log in."
    if "crop" in u:
        return "Select your main crop (cotton, paddy, wheat, tomato, soybean). The AI uses this for personalized advice."
    if "district" in u or "location" in u:
        return "Enter your district name — we use it for weather, soil, and mandi price context."
    if "username" in u:
        return "Pick a unique username (letters, numbers, underscore). Example: farmer_ramesh_2026"
    return (
        "Welcome to GreenHarvest! Fill in: **display name**, **username**, **password**, "
        "**district**, and **crop**. Then click **Create account**. "
        "You can ask me about any field while you sign up."
    )


def _parse_crop_from_user(user: str) -> str:
    for line in user.splitlines():
        if line.strip().lower().startswith("query:"):
            q = line.split(":", 1)[1].lower()
            for c in ["cotton", "paddy", "wheat", "tomato", "soybean", "rice"]:
                if c in q:
                    return "paddy" if c == "rice" else c
    m = re.search(r'"crop"\s*:\s*"(\w+)"', user, re.I)
    if m:
        return m.group(1).lower()
    return ""


def _crop_offline_json(query: str, lower: str, crop_hint: str = "") -> str:
    crop = crop_hint
    if not crop:
        for c in ["cotton", "paddy", "wheat", "tomato", "soybean", "rice"]:
            if c in lower:
                crop = "paddy" if c == "rice" else c
                break
    chunks = retrieve(query, crop=crop, top_k=3)
    if chunks:
        steps = []
        for i, ch in enumerate(chunks[:3], 1):
            snippet = ch["text"][:280].strip()
            steps.append(f"{i}. {snippet}")
        rec = "\n".join(steps)
        source = chunks[0].get("metadata", {}).get("source", "local guide")
    else:
        rec = (
            "Consult your nearest Krishi Vigyan Kendra or field officer. "
            "Describe symptoms, crop stage, and district for best help."
        )
        source = "offline template"

    return json.dumps({
        "recommendation": rec,
        "safety_notes": f"Offline mode — verify advice with an expert. Source: {source}",
        "confidence": 0.42 if chunks else 0.3,
    })


def _crop_offline_text(query: str, lower: str, crop_hint: str = "") -> str:
    crop = crop_hint
    if not crop:
        for c in ["cotton", "paddy", "wheat", "tomato", "soybean"]:
            if c in lower:
                crop = c
                break
    chunks = retrieve(query, crop=crop, top_k=2)
    if chunks:
        body = chunks[0]["text"][:600]
        src = chunks[0].get("metadata", {}).get("source", "GreenHarvest KB")
        return (
            f"**GreenHarvest advisory (offline — local guides)**\n\n{body}\n\n"
            f"*Source: {src}. Please confirm with a field officer before applying chemicals.*"
        )
    return (
        "**GreenHarvest (offline)**\n\n"
        "No internet or API keys available. Your query was saved locally. "
        "General tip: note crop stage, symptoms, and district — then contact your field officer. "
        "When online, full Gen AI returns automatically."
    )
