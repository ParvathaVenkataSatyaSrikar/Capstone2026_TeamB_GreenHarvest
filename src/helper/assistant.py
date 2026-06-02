"""Portal Assistant — FAQ first, then LangChain LCEL chain for application help."""
from src.chains.agri_chains import build_guide_chain
from src.helper.context import build_helper_context
from src.helper.knowledge_base import offline_guide_answer, match_faq
from src.i18n.guide_strings import fast_guide_answer
from src.i18n.language import is_english, language_directive, normalize_language
from src.ui.branding import GUIDE_NAME


def _is_crop_leak(text: str) -> bool:
    if not text:
        return True
    markers = (
        "greenharvest advisory (offline",
        "local guides",
        "cotton.md",
        "yellowing leaves",
    )
    t = text.lower()
    return any(m in t for m in markers)


def ask_guide(
    role: str,
    question: str,
    page_name: str = "",
    history: list | None = None,
    language: str = "english",
    user: dict | None = None,
) -> str:
    lang = normalize_language(language)

    instant = fast_guide_answer(role, question, user, lang)
    if instant:
        return instant

    from src.helper.live_context import try_operational_answer

    operational = try_operational_answer(role, question, user, page_name)
    if operational:
        return operational

    if is_english(lang):
        hit = match_faq(question, role)
        if hit:
            return hit
        broad = any(p in question.lower() for p in ("how to use", "use the app", "how do i use"))
        if broad:
            from src.helper.knowledge_base import FULL_GUIDES
            return FULL_GUIDES.get(role, FULL_GUIDES["farmer"])

    system = build_helper_context(role, page_name, user=user, compact=True)
    system += (
        f"\n\nYou are {GUIDE_NAME} — app help only, not crop advice.\n"
        "Use LIVE APP DATA numbers exactly. Be concise.\n"
        f"{language_directive(lang)}"
    )
    if history:
        for msg in history[-4:]:
            role_tag = "User" if msg["role"] == "user" else "Assistant"
            system += f"\n{role_tag}: {msg['content'][:400]}"

    try:
        chain = build_guide_chain()
        text = chain.invoke({"system": system, "question": question}).strip()
        meta_offline = "offline" in text.lower() and len(text) < 80
        if text and not meta_offline and not _is_crop_leak(text) and len(text) > 40:
            if text and "Configure API" not in text:
                return text
    except Exception:
        pass

    return offline_guide_answer(role, question)


ask_helper = ask_guide
