"""Offline FAQ and application guides for Portal Assistant."""

from src.ui.branding import GUIDE_NAME, CROP_ADVISOR_NAME

FARMER_FULL_GUIDE = f"""## How to use GreenHarvest (farmer)

### 1. Sign in
- Open the **Login** page.
- Choose the **Farmer** tab.
- Enter username and password → **Sign in as Farmer**.
- Demo: `farmer_f001` / `farmer123`

### 2. Farmer Home
- Your dashboard: how many questions you asked, how many are **with an expert**, and shortcuts.
- **Start chatting** → opens **{CROP_ADVISOR_NAME}**.
- **View history** → opens **My Queries**.

### 3. {CROP_ADVISOR_NAME} (farming questions)
- Ask in plain language: pests, water, fertilizer, prices, government schemes.
- **Chat** tab: ask questions; your history **saves automatically** when you return.
- **My farm** tab: update crop, district, and stage; see weather and soil tips.
- **Instant answer** — routine questions answered right away.
- **With agriculture expert** — pests, insurance, or urgent cases; an officer reviews first.

### 4. My Queries
- Every question you ever asked.
- See status: instant answer, waiting for expert, or expert approved.
- If something is **with an expert**, the full answer appears here after approval.

### 5. {GUIDE_NAME} (this help)
- Explains the app only — **not** crop treatment.
- Open from the sidebar: **Open {GUIDE_NAME}**.

### 6. Language
- Change **Language** at the top of the sidebar.

### 7. Log out
- **Logout** at the bottom of the sidebar when you are done.
"""

OFFICER_FULL_GUIDE = f"""## How to use GreenHarvest (field officer)

### 1. Sign in
- **Login** → **Field Officer** tab → username and password.
- Demo: `officer1` / `officer2026`

### 2. Officer Home
- See how many farmer questions need your review.
- Open **Human Review** or **Field Cases**.

### 3. Human Review
- Queue of AI drafts waiting for you.
- Read the farmer question and draft answer.
- Edit if needed → **Approve** (farmer sees it in My Queries) or **Reject** (officer follow-up).

### 4. Field Cases
- Escalated cases and field visit notes.

### 5. {GUIDE_NAME}
- Sidebar → **Open {GUIDE_NAME}** for app help.
"""

ADMIN_FULL_GUIDE = f"""## How to use GreenHarvest (admin)

### 1. Sign in
- **Login** → **Admin** tab. Demo: `admin` / `admin2026`

### 2. Admin Home
- Shortcuts to all admin tools.

### 3. Main pages
- **Analytics** — charts, query trends, alerts.
- **Governance** — audit log and export.
- **Knowledge Base** — upload crop documents used by {CROP_ADVISOR_NAME}.
- **Settings** — test AI connection, reset demo data (administrator only).

### 4. {GUIDE_NAME}
- Sidebar → **Open {GUIDE_NAME}** for navigation help.
"""

FULL_GUIDES = {
    "farmer": FARMER_FULL_GUIDE,
    "field_officer": OFFICER_FULL_GUIDE,
    "admin": ADMIN_FULL_GUIDE,
}

FAQ: list[tuple[list[str], str]] = [
    (
        ["how long", "time", "wait", "when will", "how soon", "review time", "answer time", "how much time"],
        """### How long for answers?

**Instant** — routine questions: seconds in **AI Crop Advisor**.

**Expert review** — pests, insurance, urgent cases: usually **same day to 1–2 working days**.

Track status in **My Queries** and watch for alerts on **Farmer Home**.""",
    ),
    (
        ["how to use", "use the app", "use application", "use this app", "get started", "tutorial", "walk me through", "explain the app", "how do i use"],
        "",  # filled by role in match_faq
    ),
    (
        ["login", "sign in", "password", "username", "demo", "account"],
        """### Sign in
1. Open **Login**.
2. Pick your role tab: Farmer, Field Officer, or Admin.
3. Enter username and password.

**Demo farmer:** `farmer_f001` / `farmer123`  
**Demo officer:** `officer1` / `officer2026`  
**Demo admin:** `admin` / `admin2026`

Stay in one portal until **Logout**.""",
    ),
    (
        ["sign up", "signup", "register", "new farmer", "create account"],
        """### New farmer account
1. From Login, go to **Sign Up**.
2. Enter name, username, password, district, crop, language.
3. **Create account** — you land on Farmer Home.

Officers and admins are created by your organization.""",
    ),
    (
        ["crop advisor", "ask question", "chat", "advice", "pest", "where ask", "farming question"],
        f"""### {CROP_ADVISOR_NAME}
- Menu → **{CROP_ADVISOR_NAME}** for pests, irrigation, prices, schemes.
- **{GUIDE_NAME}** (sidebar) is only for app help — not crop advice.
- Include crop, district, and your problem for better answers.""",
    ),
    (
        ["review", "expert", "pending", "waiting", "approve", "human", "officer", "why expert"],
        """### Instant answer vs expert review

**Instant answer** — routine questions; you see the full reply in chat immediately.

**With agriculture expert** — when:
- Topic is pest/disease or crop insurance
- Your message sounds urgent (outbreak, emergency, severe)
- The system needs a human double-check

Check **My Queries** for status. A field officer approves on **Human Review**.""",
    ),
    (
        ["my queries", "history", "past question", "previous", "where answer"],
        """### My Queries
- Menu → **My Queries** — all your questions.
- **Instant answer** — already shared with you.
- **With expert** — officer still reviewing.
- **Expert approved** — full answer is here.

Chat history in Crop Advisor also reloads when you sign in again.""",
    ),
    (
        ["profile", "crop", "district", "farm", "update"],
        """### Update farm profile
1. **AI Crop Advisor** → **My farm** tab.
2. Change crop, district, crop stage.
3. **Save profile**.""",
    ),
    (
        ["language", "hindi", "telugu", "tamil", "marathi", "punjabi"],
        """### Language
Use the **Language** dropdown at the top of the sidebar. Crop Advisor tries to reply in that language.""",
    ),
    (
        ["officer", "field officer", "approve", "reject", "human review"],
        """### Officer: approve a query
1. **Human Review** from the menu.
2. Open a pending case.
3. Edit the draft if needed.
4. **Approve** → farmer sees answer in My Queries.
5. **Reject** → farmer is told an officer will follow up.""",
    ),
    (
        ["admin", "analytics", "governance", "knowledge", "settings"],
        """### Admin pages
- **Analytics** — usage and alerts
- **Governance** — audit logs
- **Knowledge Base** — crop documents
- **Settings** — tests and demo reset""",
    ),
    (
        ["who are you", "what are you", "your friend", "friend", "guide", "krishi guide"],
        f"""I am **{GUIDE_NAME}** — I explain how to use GreenHarvest.

I do **not** give crop or pest advice. Use **{CROP_ADVISOR_NAME}** for farming questions.""",
    ),
    (
        ["home", "dashboard", "farmer home", "start"],
        """### Farmer Home
Dashboard with your stats and buttons to **AI Crop Advisor** and **My Queries**.""",
    ),
    (
        ["logout", "log out", "switch role"],
        """### Log out
Click **Logout** in the sidebar. Each account is one role only — sign out to switch.""",
    ),
]


def _score(question: str, keywords: list[str]) -> int:
    q = question.lower()
    return sum(1 for k in keywords if k in q)


def match_faq(question: str, role: str = "farmer") -> str | None:
    q = question.lower()
    broad_keywords = FAQ[1][0]  # "how to use" entry — not timing FAQ
    if _score(q, broad_keywords) >= 1:
        return FULL_GUIDES.get(role, FARMER_FULL_GUIDE)

    best_score = 0
    best_answer = None
    for keywords, answer in FAQ:
        if not answer:
            continue
        s = _score(q, keywords)
        if s > best_score:
            best_score = s
            best_answer = answer
    if best_score >= 1:
        return best_answer
    return None


def offline_guide_answer(role: str, question: str, force_full: bool = False) -> str:
    if force_full:
        return FULL_GUIDES.get(role, FARMER_FULL_GUIDE)
    hit = match_faq(question, role)
    if hit:
        return hit
    role_hint = {
        "farmer": f"Open **{CROP_ADVISOR_NAME}** for farming questions, or **My Queries** for history.",
        "field_officer": "Open **Human Review** for the approval queue.",
        "admin": "Use **Analytics**, **Governance**, or **Knowledge Base** from the menu.",
    }.get(role, "Use the sidebar menu for your role.")
    return (
        f"**{GUIDE_NAME}** helps with navigation and how the app works.\n\n"
        f"For your role: {role_hint}\n\n"
        f"Try: *How do I use this app?* or *Why is my answer with an expert?*"
    )


offline_helper_answer = offline_guide_answer
