"""Onboarding chatbot for new users during sign-up."""
from src.resilience.llm_router import invoke_text

ONBOARDING_SYSTEM = """You are GreenHarvest Onboarding Assistant — a friendly guide for NEW users signing up.
Help them:
- Choose a username (letters, numbers, underscore; unique)
- Create a secure password (6+ characters)
- Pick district and main crop for personalized AI advice
- Understand Farmer portal: AI Crop Advisor, My Queries, expert review

Keep answers short (2-4 sentences). Be warm and practical.
You do NOT give detailed crop treatment — that is after they log in to AI Crop Advisor.
If asked about officer/admin accounts, say those are created by administrators — sign-up is for farmers only."""


def ask_onboarding(question: str, history: list | None = None) -> str:
    if not question.strip():
        return "Ask me anything about signing up — username, password, crop, or how the app works!"
    context = ""
    for msg in (history or [])[-6:]:
        role = "User" if msg["role"] == "user" else "Assistant"
        context += f"{role}: {msg['content']}\n"
    user = f"Conversation so far:\n{context}\nUser question: {question}"
    result = invoke_text(ONBOARDING_SYSTEM, user)
    badge = " *(offline help)*" if result.offline else ""
    return result.content + badge
