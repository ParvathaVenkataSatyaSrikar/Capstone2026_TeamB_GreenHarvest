"""
Demo farmers, field officers, and sample interactions for analytics and demonstrations.

All demo farmers: username farmer_f### (e.g. farmer_f001), password farmer123
All demo officers: username officer1..officer5, password officer2026
"""
from __future__ import annotations

import hashlib
import random
import sqlite3
import time
from datetime import datetime, timedelta

from src.db.repository import get_connection

USERS_SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL,
    farmer_id TEXT,
    display_name TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now'))
);
"""


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.strip().encode("utf-8")).hexdigest()

# farmer_id, name, district, crop, land_acres, irrigation, language, crop_stage, phone
DEMO_FARMERS: list[tuple] = [
    ("F001", "Ramesh Kumar", "Warangal", "cotton", 3.5, "drip", "telugu", "flowering", "9876500001"),
    ("F002", "Sunita Devi", "Guntur", "paddy", 2.0, "canal", "telugu", "tillering", "9876500002"),
    ("F003", "Vikram Singh", "Nashik", "tomato", 1.2, "drip", "hindi", "harvest", "9876500003"),
    ("F004", "Anita Patil", "Akola", "soybean", 4.0, "rainfed", "marathi", "pod_fill", "9876500004"),
    ("F005", "Mohan Lal", "Jalandhar", "wheat", 5.0, "canal", "punjabi", "grain_fill", "9876500005"),
    ("F006", "Lakshmi Reddy", "Kurnool", "cotton", 2.8, "sprinkler", "telugu", "vegetative", "9876500006"),
    ("F007", "Rajesh Yadav", "Meerut", "sugarcane", 6.2, "canal", "hindi", "vegetative", "9876500007"),
    ("F008", "Priya Nair", "Thrissur", "coconut", 3.0, "rainfed", "malayalam", "mature", "9876500008"),
    ("F009", "Hassan Ali", "Mysuru", "ragi", 1.5, "rainfed", "kannada", "tillering", "9876500009"),
    ("F010", "Geeta Sharma", "Jaipur", "mustard", 2.4, "sprinkler", "hindi", "flowering", "9876500010"),
    ("F011", "Arun Das", "Bhubaneswar", "paddy", 3.1, "canal", "odia", "vegetative", "9876500011"),
    ("F012", "Meena Kumari", "Patna", "maize", 2.2, "rainfed", "hindi", "grain_fill", "9876500012"),
    ("F013", "Suresh Patel", "Ahmedabad", "groundnut", 3.8, "drip", "gujarati", "pod_fill", "9876500013"),
    ("F014", "Kamala Devi", "Raipur", "pigeon pea", 2.6, "rainfed", "hindi", "flowering", "9876500014"),
    ("F015", "Joseph Thomas", "Idukki", "tea", 1.0, "sprinkler", "malayalam", "vegetative", "9876500015"),
    ("F016", "Fatima Begum", "Hyderabad", "chilli", 1.8, "drip", "telugu", "harvest", "9876500016"),
    ("F017", "Balwant Singh", "Ludhiana", "wheat", 4.5, "canal", "punjabi", "tillering", "9876500017"),
    ("F018", "Deepa Rao", "Vijayawada", "paddy", 2.9, "canal", "telugu", "flowering", "9876500018"),
    ("F019", "Imran Khan", "Lucknow", "potato", 2.1, "sprinkler", "hindi", "vegetative", "9876500019"),
    ("F020", "Lata Menon", "Kolhapur", "sugarcane", 5.5, "drip", "marathi", "mature", "9876500020"),
    ("F021", "Chandan Oraon", "Ranchi", "tomato", 1.4, "rainfed", "hindi", "flowering", "9876500021"),
    ("F022", "Pooja Verma", "Indore", "soybean", 3.3, "sprinkler", "hindi", "pod_fill", "9876500022"),
    ("F023", "Murugan S", "Coimbatore", "banana", 2.0, "drip", "tamil", "vegetative", "9876500023"),
    ("F024", "Ayesha Khatun", "Malda", "paddy", 2.7, "canal", "bengali", "vegetative", "9876500024"),
    ("F025", "Harpreet Kaur", "Amritsar", "cotton", 3.9, "drip", "punjabi", "boll_formation", "9876500025"),
]

DEMO_OFFICERS: list[tuple] = [
    ("U-OFF1", "officer1", "officer2026", "field_officer", None, "Field Officer Rao"),
    ("U-OFF2", "officer2", "officer2026", "field_officer", None, "Priya Sharma"),
    ("U-OFF3", "officer3", "officer2026", "field_officer", None, "Arjun Mehta"),
    ("U-OFF4", "officer4", "officer2026", "field_officer", None, "Kavitha N"),
    ("U-OFF5", "officer5", "officer2026", "field_officer", None, "Sanjay Pillai"),
]

DEMO_ADMIN = ("U-ADM1", "admin", "admin2026", "admin", None, "System Admin")

FARMER_PASSWORD = "farmer123"

_SAMPLE_QUERIES: list[tuple[str, str, str, float, bool]] = [
    ("Whiteflies on cotton leaves", "pest_disease", "telugu", 0.72, False),
    ("When to apply urea for paddy", "crop_advisory", "telugu", 0.81, False),
    ("Wheat irrigation in current weather", "irrigation", "punjabi", 0.85, False),
    ("Bollworm damage on young plants", "pest_disease", "telugu", 0.75, False),
    ("Tomato leaf curl symptoms", "pest_disease", "hindi", 0.68, True),
    ("Minimum support price for soybean", "market", "marathi", 0.77, False),
    ("PM-KISAN eligibility check", "scheme", "hindi", 0.80, False),
    ("Drip schedule for chilli in summer", "irrigation", "telugu", 0.83, False),
    ("Yellow spots on paddy leaves", "pest_disease", "odia", 0.70, False),
    ("Organic fertilizer for vegetables", "crop_advisory", "hindi", 0.79, False),
    ("Mandi rate for wheat today", "market", "punjabi", 0.74, False),
    ("Crop insurance claim process", "scheme", "hindi", 0.71, True),
    ("Sugarcane ratoon management", "crop_advisory", "hindi", 0.82, False),
    ("Aphids on mustard — safe spray", "pest_disease", "hindi", 0.76, False),
    ("Soil testing near my village", "crop_advisory", "kannada", 0.78, False),
]

_demo_accounts_seeded = False


def _upsert_user(
    conn,
    user_id: str,
    username: str,
    password: str,
    role: str,
    farmer_id: str | None,
    display_name: str,
) -> None:
    conn.execute(
        """INSERT INTO users (user_id, username, password_hash, role, farmer_id, display_name)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(username) DO UPDATE SET
            user_id=excluded.user_id,
            password_hash=excluded.password_hash,
            role=excluded.role,
            farmer_id=excluded.farmer_id,
            display_name=excluded.display_name""",
        (user_id, username.lower(), _hash_password(password), role, farmer_id, display_name),
    )


def _demo_roster_complete() -> bool:
    """True if DB already has the full demo farmer + officer roster."""
    try:
        with get_connection() as conn:
            farmers = conn.execute(
                "SELECT COUNT(*) FROM users WHERE role = 'farmer'"
            ).fetchone()[0]
            officers = conn.execute(
                "SELECT COUNT(*) FROM users WHERE role = 'field_officer'"
            ).fetchone()[0]
        return farmers >= len(DEMO_FARMERS) and officers >= len(DEMO_OFFICERS)
    except Exception:
        return False


def ensure_demo_farmers_and_officers(*, seed_interactions: bool = True) -> dict:
    """Upsert 25 farmers + 5 officers (+ admin). Skips if roster already present."""
    global _demo_accounts_seeded
    if _demo_accounts_seeded or _demo_roster_complete():
        _demo_accounts_seeded = True
        return {"skipped": True}

    stats = {"farmers": 0, "officers": 0, "interactions_added": 0}

    last_err: Exception | None = None
    for attempt in range(6):
        try:
            _run_demo_upsert(stats)
            last_err = None
            break
        except sqlite3.OperationalError as exc:
            last_err = exc
            if "locked" not in str(exc).lower() or attempt >= 5:
                raise
            time.sleep(0.4 * (attempt + 1))
    if last_err:
        raise last_err

    if seed_interactions:
        stats["interactions_added"] = _seed_sample_interactions()

    _demo_accounts_seeded = True
    return stats


def _run_demo_upsert(stats: dict) -> None:
    with get_connection() as conn:
        conn.execute(USERS_SCHEMA)
        for row in DEMO_FARMERS:
            fid, name, district, crop, acres, irr, lang, stage, phone = row
            conn.execute(
                """INSERT INTO farmers
                (farmer_id, name, district, crop, land_acres, irrigation_type, language, crop_stage, phone)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(farmer_id) DO UPDATE SET
                name=excluded.name, district=excluded.district, crop=excluded.crop,
                land_acres=excluded.land_acres, irrigation_type=excluded.irrigation_type,
                language=excluded.language, crop_stage=excluded.crop_stage, phone=excluded.phone""",
                (fid, name, district, crop, acres, irr, lang, stage, phone),
            )
            num = fid[1:]
            username = f"farmer_f{num.lower()}"
            _upsert_user(
                conn, f"U-{fid}", username, FARMER_PASSWORD,
                "farmer", fid, name,
            )
            stats["farmers"] += 1

        for uid, username, pwd, role, farmer_id, name in DEMO_OFFICERS:
            _upsert_user(conn, uid, username, pwd, role, farmer_id, name)
            stats["officers"] += 1

        uid, username, pwd, role, farmer_id, name = DEMO_ADMIN
        _upsert_user(conn, uid, username, pwd, role, farmer_id, name)


def _seed_sample_interactions(min_total: int = 45) -> int:
    """Add diverse interactions for Admin Analytics charts (idempotent)."""
    with get_connection() as conn:
        total = conn.execute("SELECT COUNT(*) FROM interactions").fetchone()[0]
    if total >= min_total:
        return 0

    farmer_ids = [f[0] for f in DEMO_FARMERS]
    farmer_by_id = {f[0]: f for f in DEMO_FARMERS}
    random.seed(42)
    added = 0
    base = datetime.utcnow() - timedelta(days=14)
    rows_to_insert = []

    for i in range(min_total - total):
        fid = random.choice(farmer_ids)
        row = farmer_by_id[fid]
        district, crop, lang = row[2], row[3], row[6]
        q, intent, q_lang, conf, esc = random.choice(_SAMPLE_QUERIES)
        lang_use = lang if random.random() > 0.3 else q_lang
        review = "pending_human" if esc and random.random() > 0.5 else "auto_approved"
        created = (base + timedelta(hours=i * 7)).strftime("%Y-%m-%d %H:%M:%S")
        response = (
            f"Demo guidance for {crop} in {district}: follow local extension advice "
            f"and monitor the field every 2–3 days."
        )
        rows_to_insert.append(
            (fid, q, response, intent, lang_use, conf, int(esc), review, created),
        )

    if rows_to_insert:
        with get_connection() as conn:
            conn.executemany(
                """INSERT INTO interactions
                (farmer_id, query_text, response_text, intent, language, confidence,
                 escalated, review_status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                rows_to_insert,
            )
        added = len(rows_to_insert)
    return added


def list_demo_farmer_logins() -> list[dict]:
    """For docs / admin — first 5 + count."""
    return [
        {"username": f"farmer_f{fid[1:].lower()}", "password": FARMER_PASSWORD, "name": name}
        for fid, name, *_ in DEMO_FARMERS[:5]
    ]
