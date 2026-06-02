"""Instant Portal Assistant answers — all languages, no API wait."""
from __future__ import annotations

from src.i18n.language import normalize_language
from src.ui.branding import GUIDE_NAME, GUIDE_NAME_BY_LANG

# --- Welcome (instant on language switch) ---

FARMER_GUIDE_WELCOME = {
    "english": (
        "Welcome to **Portal Assistant**.\n\n"
        "**Your status:** {total} questions · **{pending}** with expert review.\n\n"
        "I explain the application — for crop advice use **AI Crop Advisor**."
    ),
    "hindi": (
        "**पोर्टल सहायक** में आपका स्वागत है।\n\n"
        "**आपकी स्थिति:** {total} प्रश्न · **{pending}** विशेषज्ञ समीक्षा में।\n\n"
        "मैं ऐप समझाता हूँ — फसल सलाह के लिए **AI Crop Advisor** खोलें।"
    ),
    "telugu": (
        "**పోర్టల్ సహాయకుడు**కి స్వాగతం.\n\n"
        "**మీ స్థితి:** {total} ప్రశ్నలు · **{pending}** నిపుణుల సమీక్షలో.\n\n"
        "నేను యాప్ వివరిస్తాను — పంట సలహా కోసం **AI Crop Advisor** ఉపయోగించండి."
    ),
    "tamil": (
        "**போர்டல் உதவியாளர்**க்கு வரவேற்கிறோம்.\n\n"
        "**உங்கள் நிலை:** {total} கேள்விகள் · **{pending}** நிபுணர் மதிப்பீட்டில்.\n\n"
        "பயன்பாட்டை நான் விளக்குகிறேன் — பயிர் ஆலோசனைக்கு **AI Crop Advisor** பயன்படுத்துங்கள்."
    ),
    "marathi": (
        "**पोर्टल सहाय्यक** मध्ये स्वागत आहे.\n\n"
        "**तुमची स्थिती:** {total} प्रश्न · **{pending}** तज्ज्ञ पुनरावलोकनात.\n\n"
        "मी अॅप समजावतो — पिक सल्ल्यासाठी **AI Crop Advisor** वापरा."
    ),
    "punjabi": (
        "**ਪੋਰਟਲ ਸਹਾਇਕ** ਵਿੱਚ ਜੀ ਆਇਆਂ ਨੂੰ।\n\n"
        "**ਤੁਹਾਡੀ ਸਥਿਤੀ:** {total} ਸਵਾਲ · **{pending}** ਮਾਹਿਰ ਸਮੀਖਿਆ ਵਿੱਚ।\n\n"
        "ਮੈਂ ਐਪ ਸਮਝਾਉਂਦਾ ਹਾਂ — ਫਸਲ ਸਲਾਹ ਲਈ **AI Crop Advisor** ਵਰਤੋ।"
    ),
}

FARMER_GUIDE_WELCOME_NO_ID = {
    "english": "Welcome to **Portal Assistant**.\n\nI explain the application — use **AI Crop Advisor** for crop questions.",
    "hindi": "**पोर्टल सहायक** में स्वागत। एप्लिकेशन सहायता यहाँ — फसल सलाह **AI Crop Advisor** में।",
    "telugu": "**పోర్టల్ సహాయకుడు**కి స్వాగతం. అప్లికేషన్ సహాయం ఇక్కడ — పంట సలహా **AI Crop Advisor**.",
    "tamil": "**போர்டல் உதவியாளர்** வரவேற்பு. பயன்பாட்ட உதவி இங்கே — பயிர் **AI Crop Advisor**.",
    "marathi": "**पोर्टल सहाय्यक** स्वागत. अॅप मदत येथे — पिक सल्ला **AI Crop Advisor**.",
    "punjabi": "**ਪੋਰਟਲ ਸਹਾਇਕ** — ਐਪਲੀਕੇਸ਼ਨ ਮਦਦ ਇੱਥੇ; ਫਸਲ ਸਲਾਹ **AI Crop Advisor**.",
}

# --- Timing answer (quick button #1) ---

FARMER_TIMING = {
    "english": (
        "## How long until I get an answer?\n\n"
        "**Instant** — routine questions: seconds in **AI Crop Advisor**.\n\n"
        "**Expert review** — pests, insurance, urgent cases: usually **same day to 1–2 working days**.\n\n"
        "**Your account now:** **{pending}** waiting for expert review.\n\n"
        "Check **My Queries** for status."
    ),
    "hindi": (
        "## उत्तर में कितना समय?\n\n"
        "**तुरंत** — सामान्य प्रश्न: **AI Crop Advisor** में कुछ सेकंड।\n\n"
        "**विशेषज्ञ समीक्षा** — कीट, बीमा, जरूरी: आमतौर पर **1–2 कार्य दिवस**।\n\n"
        "**अभी आपके:** **{pending}** विशेषज्ञ समीक्षा में।\n\n"
        "स्थिति **My Queries** में देखें।"
    ),
    "telugu": (
        "## సమాధానానికి ఎంత సమయం?\n\n"
        "**త్వరిత** — సాధారణ ప్రశ్నలు: **AI Crop Advisor**లో కొన్ని సెకన్లు.\n\n"
        "**నిపుణుల సమీక్ష** — పురుగు, భీమా, అత్యవసరం: సాధారణంగా **1–2 పని దినాలు**.\n\n"
        "**మీ ఖాతా:** **{pending}** నిపుణుల సమీక్షలో.\n\n"
        "స్థితి **My Queries**లో చూడండి."
    ),
    "tamil": (
        "## பதில் எவ்வளவு நேரம்?\n\n"
        "**உடனடி** — சாதாரண கேள்விகள்: **AI Crop Advisor**-ல் சில வினாடிகள்.\n\n"
        "**நிபுணர் மதிப்பீடு** — பூச்சி, காப்பீடு: பொதுவாக **1–2 நாட்கள்**.\n\n"
        "**உங்கள் கணக்கு:** **{pending}** காத்திருக்கிறது.\n\n"
        "**My Queries**-ல் பாருங்கள்."
    ),
    "marathi": (
        "## उत्तर किती वेळ?\n\n"
        "**त्वरित** — सामान्य प्रश्न: **AI Crop Advisor** मध्ये सेकंद.\n\n"
        "**तज्ज्ञ पुनरावलोकन** — कीड, विमा: साधारण **1–2 कार्यदिवस**.\n\n"
        "**तुमचे:** **{pending}** प्रलंबित.\n\n"
        "**My Queries** मध्ये तपासा."
    ),
    "punjabi": (
        "## ਜਵਾਬ ਕਿੰਨਾ ਸਮਾਂ?\n\n"
        "**ਤੁਰੰਤ** — ਆਮ ਸਵਾਲ: **AI Crop Advisor** ਵਿੱਚ ਸਕਿੰਟ.\n\n"
        "**ਮਾਹਿਰ ਸਮੀਖਿਆ** — ਕੀੜੇ, ਬੀਮਾ: ਆਮ **1–2 ਦਿਨ**.\n\n"
        "**ਤੁਹਾਡੇ:** **{pending}** ਲੰਬਿਤ.\n\n"
        "**My Queries** ਵਿੱਚ ਦੇਖੋ."
    ),
}

# --- Status answer (quick button #3) ---

FARMER_STATUS = {
    "english": (
        "## Your query status\n\n"
        "- **Total questions:** {total}\n"
        "- **Asked today:** {today}\n"
        "- **With expert:** **{pending}**\n\n{extra}"
    ),
    "hindi": (
        "## आपकी स्थिति\n\n"
        "- **कुल प्रश्न:** {total}\n"
        "- **आज:** {today}\n"
        "- **विशेषज्ञ के पास:** **{pending}**\n\n{extra}"
    ),
    "telugu": (
        "## మీ స్థితి\n\n"
        "- **మొత్తం ప్రశ్నలు:** {total}\n"
        "- **ఈ రోజు:** {today}\n"
        "- **నిపుణుల వద్ద:** **{pending}**\n\n{extra}"
    ),
    "tamil": (
        "## உங்கள் நிலை\n\n"
        "- **மொத்த கேள்விகள்:** {total}\n"
        "- **இன்று:** {today}\n"
        "- **நிபுணரிடம்:** **{pending}**\n\n{extra}"
    ),
    "marathi": (
        "## तुमची स्थिती\n\n"
        "- **एकूण प्रश्न:** {total}\n"
        "- **आज:** {today}\n"
        "- **तज्ज्ञाकडे:** **{pending}**\n\n{extra}"
    ),
    "punjabi": (
        "## ਤੁਹਾਡੀ ਸਥਿਤੀ\n\n"
        "- **ਕੁੱਲ ਸਵਾਲ:** {total}\n"
        "- **ਅੱਜ:** {today}\n"
        "- **ਮਾਹਿਰ ਕੋਲ:** **{pending}**\n\n{extra}"
    ),
}

FARMER_STATUS_WAITING = {
    "english": "⏳ Waiting for expert approval — see **My Queries**.",
    "hindi": "⏳ विशेषज्ञ समीक्षा — **My Queries** देखें।",
    "telugu": "⏳ నిపుణుల సమీక్ష — **My Queries** చూడండి.",
    "tamil": "⏳ நிபுணர் மதிப்பீடு — **My Queries**.",
    "marathi": "⏳ तज्ज्ञ पुनरावलोकन — **My Queries**.",
    "punjabi": "⏳ ਮਾਹਿਰ ਸਮੀਖਿਆ — **My Queries**.",
}

FARMER_STATUS_CLEAR = {
    "english": "✅ Nothing waiting for expert review.",
    "hindi": "✅ विशेषज्ञ समीक्षा में कुछ नहीं।",
    "telugu": "✅ నిపుణుల సమీక్షలో ఏమీ లేదు.",
    "tamil": "✅ காத்திருப்பு இல்லை.",
    "marathi": "✅ प्रलंबित नाही.",
    "punjabi": "✅ ਕੋਈ ਲੰਬਿਤ ਨਹੀਂ.",
}

# --- How to use (quick button #2) ---

def _how_to_step5(lang: str) -> str:
    name = GUIDE_NAME_BY_LANG.get(lang, GUIDE_NAME)
    return f"5. **{name}** (sidebar) — app help only\n"


FARMER_HOW_TO = {
    "english": (
        "## How to use GreenHarvest\n\n"
        "1. **Login** → Farmer tab → sign in (`farmer_f001` / `farmer123` demo)\n"
        "2. **Farmer Home** — dashboard and shortcuts\n"
        "3. **AI Crop Advisor** — ask farming questions (pests, water, fertilizer)\n"
        "4. **My Queries** — all past questions and expert review status\n"
        + _how_to_step5("english")
        + "6. **Language** — change answer language in sidebar\n"
        "7. **Logout** when done"
    ),
    "hindi": (
        "## GreenHarvest कैसे उपयोग करें\n\n"
        "1. **Login** → Farmer → साइन इन\n"
        "2. **Farmer Home** — डैशबोर्ड\n"
        "3. **AI Crop Advisor** — फसल प्रश्न\n"
        "4. **My Queries** — इतिहास और स्थिति\n"
        + _how_to_step5("hindi")
        + "6. **Language** — भाषा बदलें\n"
        "7. **Logout** — बाहर निकलें"
    ),
    "telugu": (
        "## GreenHarvest ఎలా ఉపయోగించాలి\n\n"
        "1. **Login** → Farmer → సైన్ ఇన్\n"
        "2. **Farmer Home** — డాష్‌బోర్డ్\n"
        "3. **AI Crop Advisor** — పంట ప్రశ్నలు\n"
        "4. **My Queries** — చరిత్ర & స్థితి\n"
        + _how_to_step5("telugu")
        + "6. **Language** — భాష మార్చండి\n"
        "7. **Logout** — నిష్క్రమించండి"
    ),
    "tamil": (
        "## GreenHarvest பயன்பாடு\n\n"
        "1. **Login** → Farmer → உள்நுழை\n"
        "2. **Farmer Home** — பலகை\n"
        "3. **AI Crop Advisor** — பயிர் கேள்விகள்\n"
        "4. **My Queries** — வரலாறு\n"
        + _how_to_step5("tamil")
        + "6. **Language** — மொழி\n"
        "7. **Logout**"
    ),
    "marathi": (
        "## GreenHarvest वापर\n\n"
        "1. **Login** → Farmer → साइन इन\n"
        "2. **Farmer Home** — डॅशबोर्ड\n"
        "3. **AI Crop Advisor** — पिक प्रश्न\n"
        "4. **My Queries** — इतिहास\n"
        + _how_to_step5("marathi")
        + "6. **Language** — भाषा\n"
        "7. **Logout**"
    ),
    "punjabi": (
        "## GreenHarvest ਵਰਤੋਂ\n\n"
        "1. **Login** → Farmer → ਸਾਈਨ ਇਨ\n"
        "2. **Farmer Home** — ਡੈਸ਼ਬੋਰਡ\n"
        "3. **AI Crop Advisor** — ਫਸਲ ਸਵਾਲ\n"
        "4. **My Queries** — ਇਤਿਹਾਸ\n"
        + _how_to_step5("punjabi")
        + "6. **Language** — ਭਾਸ਼ਾ\n"
        "7. **Logout**"
    ),
}

GUIDE_LANG_HINT = {
    "english": "",
    "hindi": "उत्तर हिन्दी में दिए जाएंगे।",
    "telugu": "సమాధానాలు తెలుగులో ఇవ్వబడతాయి.",
    "tamil": "பதில்கள் தமிழில் வழங்கப்படும்.",
    "marathi": "उत्तरे मराठीत दिली जातील.",
    "punjabi": "ਜਵਾਬ ਪੰਜਾਬੀ ਵਿੱਚ ਦਿੱਤੇ ਜਾਣਗੇ.",
}


def _lang(code: str) -> str:
    return normalize_language(code)


def localized_farmer_welcome(total: int, pending: int, lang: str) -> str:
    code = _lang(lang)
    return FARMER_GUIDE_WELCOME.get(code, FARMER_GUIDE_WELCOME["english"]).format(
        total=total, pending=pending
    )


def localized_farmer_welcome_simple(lang: str) -> str:
    code = _lang(lang)
    return FARMER_GUIDE_WELCOME_NO_ID.get(code, FARMER_GUIDE_WELCOME_NO_ID["english"])


def localized_timing(pending: int, lang: str) -> str:
    code = _lang(lang)
    tpl = FARMER_TIMING.get(code, FARMER_TIMING["english"])
    return tpl.format(pending=pending)


def localized_status(total: int, today: int, pending: int, lang: str) -> str:
    code = _lang(lang)
    tpl = FARMER_STATUS.get(code, FARMER_STATUS["english"])
    extra = (
        FARMER_STATUS_WAITING.get(code, FARMER_STATUS_WAITING["english"])
        if pending
        else FARMER_STATUS_CLEAR.get(code, FARMER_STATUS_CLEAR["english"])
    )
    return tpl.format(total=total, today=today, pending=pending, extra=extra)


def localized_how_to(lang: str) -> str:
    code = _lang(lang)
    return FARMER_HOW_TO.get(code, FARMER_HOW_TO["english"])


def _matches(q: str, keywords: tuple[str, ...]) -> bool:
    return any(k in q for k in keywords)


def fast_guide_answer(
    role: str,
    question: str,
    user: dict | None,
    lang: str,
) -> str | None:
    """Instant localized answer for common guide questions — no LLM."""
    q = question.lower().strip()
    code = _lang(lang)
    user = user or {}
    gname = GUIDE_NAME_BY_LANG.get(code, GUIDE_NAME)

    if role == "farmer" and user.get("farmer_id"):
        from src.db.repository import get_farmer_kpis
        fk = get_farmer_kpis(user["farmer_id"])

        if _matches(q, ("how long", "how much time", "time take", "when will", "how soon", "wait time", "expert answer")):
            return localized_timing(fk["pending_review"], code)

        if _matches(q, ("how many", "pending", "waiting", "expert", "review", "status")):
            return localized_status(
                fk["total_queries"], fk["queries_today"], fk["pending_review"], code
            )

        if _matches(q, ("how to use", "use the app", "use this app", "get started", "tutorial", "how do i use", "walk me through", "explain the app")):
            return localized_how_to(code)

        if _matches(q, ("login", "sign in", "password", "demo")):
            return localized_how_to(code).split("\n\n")[0] + "\n\nDemo: `farmer_f001` / `farmer123`"

        if _matches(q, ("crop advisor", "where ask", "farming question")):
            hints = {
                "english": f"Open **AI Crop Advisor** from the menu for crop questions. **{GUIDE_NAME}** is app help only.",
                "telugu": f"పంట ప్రశ్నలకు **AI Crop Advisor** తెరవండి. **{gname}** యాప్ సహాయం మాత్రమే.",
                "hindi": f"फसल प्रश्न **AI Crop Advisor** में। **{gname}** केवल ऐप मदद।",
            }
            return hints.get(code, hints["english"])

    if role == "farmer":
        if _matches(q, ("how to use", "use the app", "how do i use")):
            return localized_how_to(code)

    return None
