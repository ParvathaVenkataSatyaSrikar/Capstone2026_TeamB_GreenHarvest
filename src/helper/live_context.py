"""Live application data for Portal Assistant — counts, queues, and next actions."""
from __future__ import annotations

from src.db.repository import (
    get_kpis,
    get_pending_reviews,
    list_cases,
    get_farmer_kpis,
    get_farmer_notification_summary,
    get_outbreak_alerts,
    get_interactions,
)
from src.ui.branding import GUIDE_NAME


def _matches(question: str, keywords: tuple[str, ...]) -> bool:
    q = question.lower()
    return any(k in q for k in keywords)


def build_live_snapshot(role: str, user: dict | None = None, page_name: str = "") -> str:
    """Markdown block injected into every guide prompt — source of truth for counts."""
    user = user or {}
    lines = ["=== LIVE APP DATA (use these exact numbers; do not guess) ==="]

    if role == "field_officer":
        kpis = get_kpis()
        pending = get_pending_reviews()
        open_cases = list_cases(status="open")
        lines.extend([
            f"Current page: {page_name or 'unknown'}",
            f"Pending Human Review (HITL): {len(pending)}",
            f"Open field cases: {len(open_cases)}",
            f"Total system queries: {kpis['total_queries']}",
            f"Queries today: {kpis['queries_today']}",
        ])
        if pending:
            lines.append("Next pending reviews (newest first, max 5):")
            for p in pending[:5]:
                q = (p.get("query_text") or "")[:70]
                lines.append(
                    f"  - ID {p.get('interaction_id')} | {p.get('name', 'Farmer')} | "
                    f"{p.get('crop', '')} | {p.get('district', '')} | \"{q}…\""
                )
        if open_cases:
            lines.append("Open cases (max 3):")
            for c in open_cases[:3]:
                lines.append(
                    f"  - Case {c.get('case_id')} | {c.get('name')} | priority {c.get('priority')} | "
                    f"{(c.get('summary') or '')[:60]}"
                )

    elif role == "farmer":
        fid = user.get("farmer_id")
        if fid:
            fk = get_farmer_kpis(fid)
            notif = get_farmer_notification_summary(fid)
            lines.extend([
                f"Farmer ID: {fid}",
                f"Farmer name: {user.get('display_name', '')}",
                f"Total questions asked: {fk['total_queries']}",
                f"Questions today: {fk['queries_today']}",
                f"Waiting for expert review: {fk['pending_review']}",
            ])
            if notif.get("pending"):
                lines.append("Pending expert items:")
                for p in notif["pending"][:3]:
                    lines.append(f"  - \"{(p.get('query_text') or '')[:65]}…\"")
        else:
            lines.append("Farmer profile not linked to this account.")

    elif role == "admin":
        kpis = get_kpis()
        alerts = get_outbreak_alerts(active_only=True)
        lines.extend([
            f"Pending HITL system-wide: {kpis['pending_hitl']}",
            f"Open escalations: {kpis['open_escalations']}",
            f"Total queries: {kpis['total_queries']}",
            f"Queries today: {kpis['queries_today']}",
            f"Active outbreak alerts: {len(alerts)}",
        ])
        for a in alerts[:3]:
            lines.append(f"  - {a.get('district')} / {a.get('crop')}: {a.get('message', '')[:80]}")

    return "\n".join(lines)


def try_operational_answer(
    role: str,
    question: str,
    user: dict | None = None,
    page_name: str = "",
) -> str | None:
    """Direct data-driven answer for workload / count / queue questions."""
    q = question.lower().strip()
    user = user or {}

    if role == "field_officer":
        return _officer_operational(q, page_name)
    if role == "farmer":
        return _farmer_operational(q, user)
    if role == "admin":
        return _admin_operational(q)
    return None


def _officer_operational(q: str, page_name: str) -> str | None:
    kpis = get_kpis()
    pending = get_pending_reviews()
    open_cases = list_cases(status="open")
    n_pending = len(pending)
    n_cases = len(open_cases)

    count_q = _matches(
        q,
        (
            "how many", "count", "number of", "pending", "queue", "backlog",
            "waiting", "review", "hitl", "should i do", "what to do", "workload",
            "today", "priority", "next",
        ),
    )

    if count_q or "human review" in q:
        lines = [
            "## Your workload right now",
            "",
            f"| Item | Count |",
            f"|------|-------|",
            f"| **Pending Human Review** | **{n_pending}** |",
            f"| **Open field cases** | **{n_cases}** |",
            f"| Queries today (all farmers) | {kpis['queries_today']} |",
            "",
        ]

        if n_pending == 0:
            lines.append("✅ **No queries waiting** — check **Field Cases** for follow-ups.")
        else:
            lines.extend([
                f"### What you should do",
                f"1. Open **Human Review** from the menu (you have **{n_pending}** to process).",
                "2. Read each AI draft → edit if needed → **Approve** or **Reject**.",
                "3. Farmers only see answers after you approve.",
                "",
                "**Suggested pace:** work through the queue until it is clear, or at least **5–10 reviews** per session if the backlog is large.",
                "",
                "### Next in your queue",
            ])
            for i, p in enumerate(pending[:5], 1):
                snippet = (p.get("query_text") or "")[:55]
                lines.append(
                    f"{i}. **#{p.get('interaction_id')}** — {p.get('name', 'Farmer')} "
                    f"({p.get('crop', '')}, {p.get('district', '')}) — *\"{snippet}…\"*"
                )
            if n_pending > 5:
                lines.append(f"\n*…and {n_pending - 5} more on **Human Review**.*")

        if n_cases:
            lines.extend(["", f"### Field cases ({n_cases} open)", "Open **Field Cases** for escalations and visit notes."])

        return "\n".join(lines)

    if _matches(q, ("open case", "field case", "escalation")):
        if not open_cases:
            return "## Open field cases\n\nNo open cases right now. Focus on **Human Review** if pending queries exist."
        lines = [f"## Open field cases ({n_cases})", ""]
        for c in open_cases[:8]:
            lines.append(
                f"- **Case {c.get('case_id')}** — {c.get('name')} ({c.get('crop')}, {c.get('district')}) "
                f"· priority **{c.get('priority')}** · {(c.get('summary') or 'No summary')[:70]}"
            )
        lines.append("\nOpen **Field Cases** from the menu to update notes.")
        return "\n".join(lines)

    if _matches(q, ("approve", "how do i", "reject")):
        return None  # let FAQ/LLM handle process steps

    return None


def _farmer_operational(q: str, user: dict) -> str | None:
    fid = user.get("farmer_id")
    if not fid:
        return None
    fk = get_farmer_kpis(fid)
    notif = get_farmer_notification_summary(fid)

    if _matches(q, ("how long", "how much time", "time take", "when will", "how soon", "wait time", "take to answer", "take to review")):
        pending = fk["pending_review"]
        lines = [
            "## How long until I get an answer?",
            "",
            "### Instant answers",
            "Routine questions (irrigation, schemes, general care) — usually **a few seconds** in **AI Crop Advisor**.",
            "",
            "### Expert review",
            "Pests, insurance, or urgent cases go to a field officer first.",
            "- **Typical wait:** same day to **1–2 working days** (depends on officer workload).",
            f"- **Your account now:** **{pending}** question(s) waiting for expert review.",
            "",
            "### Where to check",
            "- **My Queries** — status and full approved text",
            "- Yellow banner on **Home** or **Crop Advisor** when something is waiting",
            "- Green alert when an officer approves",
            "",
            "For farming advice use **AI Crop Advisor** — I only help with the app.",
        ]
        return "\n".join(lines)

    if _matches(q, ("how many", "pending", "waiting", "expert", "review", "status")):
        lines = [
            "## Your query status",
            "",
            f"- **Total questions:** {fk['total_queries']}",
            f"- **Asked today:** {fk['queries_today']}",
            f"- **With agriculture expert:** **{fk['pending_review']}**",
            "",
        ]
        if fk["pending_review"]:
            lines.append("### Waiting for expert approval")
            for p in notif.get("pending", [])[:5]:
                lines.append(f"- *\"{(p.get('query_text') or '')[:60]}…\"*")
            lines.append("\nCheck **My Queries** — full answers appear after the officer approves.")
        else:
            lines.append("✅ Nothing waiting for expert review right now.")
        return "\n".join(lines)

    if _matches(q, ("history", "my queries", "past", "previous")):
        rows = get_interactions(farmer_id=fid, limit=5)
        lines = ["## Your recent questions", ""]
        for r in rows:
            st = r.get("review_status", "auto_approved")
            icon = "⏳" if st == "pending_human" else "✅"
            lines.append(f"{icon} {(r.get('query_text') or '')[:55]}… — **{st.replace('_', ' ')}**")
        lines.append("\nOpen **My Queries** for full history.")
        return "\n".join(lines)

    return None


def _admin_operational(q: str) -> str | None:
    kpis = get_kpis()
    alerts = get_outbreak_alerts(active_only=True)

    if _matches(q, ("how many", "pending", "stats", "overview", "dashboard", "kpi")):
        lines = [
            "## System overview (live)",
            "",
            f"- **Pending HITL:** {kpis['pending_hitl']}",
            f"- **Open escalations:** {kpis['open_escalations']}",
            f"- **Total queries:** {kpis['total_queries']}",
            f"- **Today:** {kpis['queries_today']}",
            f"- **Active outbreak alerts:** {len(alerts)}",
            "",
            "Open **Analytics** for charts, **Governance** for audit logs.",
        ]
        if alerts:
            lines.append("\n### Active alerts")
            for a in alerts[:5]:
                lines.append(f"- {a.get('district')} / {a.get('crop')}: {a.get('message', '')[:80]}")
        return "\n".join(lines)

    return None


def officer_welcome(user: dict | None = None) -> str:
    kpis = get_kpis()
    pending = get_pending_reviews()
    n = len(pending)
    name = (user or {}).get("display_name", "Officer")
    if n:
        return (
            f"Welcome, **{name}**.\n\n"
            f"**Live status:** **{n}** queries need your approval · **{len(list_cases(status='open'))}** open field cases.\n\n"
            f"Ask: *How many reviews should I do?* · *What's in my queue?* · *How do I approve?*"
        )
    return (
        f"Welcome, **{name}**.\n\n"
        "✅ No pending Human Review right now. Check **Field Cases** for follow-ups.\n\n"
        "Ask me about workflows or live system counts anytime."
    )


def farmer_welcome(user: dict | None = None) -> str:
    fid = (user or {}).get("farmer_id")
    if fid:
        fk = get_farmer_kpis(fid)
        return (
            f"Welcome to **{GUIDE_NAME}**.\n\n"
            f"**Your status:** {fk['total_queries']} questions · **{fk['pending_review']}** with expert review.\n\n"
            "I explain the application — for crop advice use **AI Crop Advisor**."
        )
    return (
        f"Welcome to **{GUIDE_NAME}**.\n\n"
        "I explain how to use GreenHarvest. For crop questions use **AI Crop Advisor**."
    )
