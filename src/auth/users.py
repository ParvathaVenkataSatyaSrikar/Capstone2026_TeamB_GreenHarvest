"""Demo user accounts (SQLite)."""
import hashlib
import re
from src.db.repository import get_connection
from config.settings import get_settings

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

# Core demo accounts — extended roster in src/auth/demo_seed.py (25 farmers, 5 officers)
DEMO_USERS = [
    ("U-F001", "farmer_f001", "farmer123", "farmer", "F001", "Ramesh Kumar"),
    ("U-F002", "farmer_f002", "farmer123", "farmer", "F002", "Sunita Devi"),
    ("U-OFF1", "officer1", "officer2026", "field_officer", None, "Field Officer Rao"),
    ("U-ADM1", "admin", "admin2026", "admin", None, "System Admin"),
]

# Optional alternate staff password (override via STAFF_DEMO_PASSWORD in .env)
DEFAULT_STAFF_DEMO_PASSWORD = "greenharvest2026"
_users_initialized = False


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.strip().encode("utf-8")).hexdigest()


def _row_to_dict(row) -> dict:
    return {k: row[k] for k in row.keys()}


def init_users(*, force: bool = False) -> None:
    """Create table and ensure all demo users exist (repair after DB reset)."""
    global _users_initialized
    if _users_initialized and not force:
        return
    with get_connection() as conn:
        conn.execute(USERS_SCHEMA)
        for uid, username, pwd, role, farmer_id, name in DEMO_USERS:
            existing = conn.execute(
                "SELECT user_id FROM users WHERE username = ?", (username,)
            ).fetchone()
            if existing:
                conn.execute(
                    """UPDATE users SET password_hash = ?, role = ?, farmer_id = ?, display_name = ?
                    WHERE username = ?""",
                    (_hash_password(pwd), role, farmer_id, name, username),
                )
            else:
                conn.execute(
                    """INSERT INTO users (user_id, username, password_hash, role, farmer_id, display_name)
                    VALUES (?, ?, ?, ?, ?, ?)""",
                    (uid, username, _hash_password(pwd), role, farmer_id, name),
                )
    if force:
        import src.auth.demo_seed as demo_seed_mod
        demo_seed_mod._demo_accounts_seeded = False
    from src.auth.demo_seed import ensure_demo_farmers_and_officers
    ensure_demo_farmers_and_officers()
    _users_initialized = True


def _password_ok(user: dict, password: str) -> bool:
    if not password:
        return False
    if _hash_password(password) == user["password_hash"]:
        return True
    if user["role"] in ("field_officer", "admin"):
        settings = get_settings()
        alt = (settings.staff_demo_password or DEFAULT_STAFF_DEMO_PASSWORD).strip()
        return password.strip() == alt
    return False


def authenticate(username: str, password: str, expected_role: str | None = None) -> dict | None:
    uname = username.strip().lower()
    if not uname or not password:
        return None

    with get_connection() as conn:
        row = conn.execute("SELECT * FROM users WHERE username = ?", (uname,)).fetchone()
    if not row:
        return None
    user = _row_to_dict(row)
    if not _password_ok(user, password):
        return None
    if expected_role and user["role"] != expected_role:
        return None
    return user


def get_user(user_id: str) -> dict | None:
    init_users()
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
    return _row_to_dict(row) if row else None


def username_available(username: str) -> bool:
    init_users()
    uname = username.strip().lower()
    if len(uname) < 4 or not re.match(r"^[a-z0-9_]+$", uname):
        return False
    with get_connection() as conn:
        row = conn.execute("SELECT 1 FROM users WHERE username = ?", (uname,)).fetchone()
    return row is None


def _next_farmer_id(conn) -> str:
    rows = conn.execute("SELECT farmer_id FROM farmers").fetchall()
    max_num = 0
    for row in rows:
        fid = row[0]
        if fid and fid.startswith("F") and fid[1:].isdigit():
            max_num = max(max_num, int(fid[1:]))
    return f"F{max_num + 1:03d}"


def register_farmer(
    username: str,
    password: str,
    display_name: str,
    district: str,
    crop: str,
    phone: str = "",
    language: str = "english",
    land_acres: float = 2.0,
    irrigation_type: str = "rainfed",
) -> tuple[dict | None, str]:
    """
    Create farmer profile + user account.
    Returns (user_dict, error_message).
    """
    init_users()
    uname = username.strip().lower()
    if not username_available(uname):
        return None, "Username invalid or already taken (use letters, numbers, underscore; min 4 chars)."
    if len(password) < 6:
        return None, "Password must be at least 6 characters."
    if not display_name.strip():
        return None, "Display name is required."
    if not district.strip():
        return None, "District is required."

    from src.rag.crop_catalog import normalize_crop, CROP_NAMES
    crop_l = normalize_crop(crop.strip().lower())
    if crop_l not in {normalize_crop(c) for c in CROP_NAMES}:
        return None, "Please select a valid crop from the list."

    with get_connection() as conn:
        farmer_id = _next_farmer_id(conn)
        user_id = f"U-{farmer_id}"
        conn.execute(
            """INSERT INTO farmers
            (farmer_id, name, district, crop, land_acres, irrigation_type, language, crop_stage, phone)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                farmer_id, display_name.strip(), district.strip(), crop_l,
                float(land_acres or 2.0), (irrigation_type or "rainfed").strip(), language, "vegetative", phone,
            ),
        )
        conn.execute(
            """INSERT INTO users (user_id, username, password_hash, role, farmer_id, display_name)
            VALUES (?, ?, ?, ?, ?, ?)""",
            (user_id, uname, _hash_password(password), "farmer", farmer_id, display_name.strip()),
        )
        row = conn.execute("SELECT * FROM users WHERE username = ?", (uname,)).fetchone()
    return (_row_to_dict(row), "") if row else (None, "Registration failed — try again.")

