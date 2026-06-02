"""Role definitions — navigation paths synced with src.auth.rbac."""
from src.auth.rbac import ROLE_NAV
from src.ui.brand import GH

ROLES = {
    "farmer": {
        "label": "Farmer",
        "icon": "🌾",
        "tagline": "Get crop advice in your language",
        "color": GH["farmer"],
        "needs_password": False,
    },
    "field_officer": {
        "label": "Field Officer",
        "icon": "👨‍🌾",
        "tagline": "Review AI drafts & manage cases",
        "color": GH["officer"],
        "needs_password": False,
    },
    "admin": {
        "label": "Admin",
        "icon": "📊",
        "tagline": "Analytics, governance & knowledge",
        "color": GH["admin"],
        "needs_password": False,
    },
}

# Single source: rbac.ROLE_NAV (includes Home pages per role)
ROLE_PAGES = ROLE_NAV

AI_MODULES = [
    ("Intake", "Captures crop, location & issue"),
    ("Intent AI", "Classifies your question type"),
    ("RAG Search", "Trusted crop guides & manuals"),
    ("Context AI", "Weather, soil & history"),
    ("Recommendation", "Personalized guidance"),
    ("Staff Summary", "Expert handoff notes"),
    ("Escalation", "Routes risky cases to humans"),
]

FARMER_QUICK_QUESTIONS = [
    "Why are my cotton leaves turning yellow?",
    "When should I irrigate wheat in current weather?",
    "What is today's tomato mandi price?",
    "How to file crop insurance after rainfall?",
    "Recommended fertilizer schedule for paddy",
]
