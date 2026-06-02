"""Data access layer for SQLite."""
import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

from config.settings import DB_PATH, DATA_DIR
from src.db.models import SCHEMA_SQL


def _configure_sqlite(conn: sqlite3.Connection) -> None:
    """WAL + busy timeout — safer with Streamlit multi-page / concurrent reads."""
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA busy_timeout=30000")


@contextmanager
def get_connection(db_path: Path | None = None):
    path = db_path or DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path), check_same_thread=False, timeout=30.0)
    conn.row_factory = sqlite3.Row
    _configure_sqlite(conn)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_schema(db_path: Path | None = None) -> None:
    with get_connection(db_path) as conn:
        conn.executescript(SCHEMA_SQL)
        _migrate_interactions(conn)
        _ensure_dealer_requests(conn)


def _migrate_interactions(conn: sqlite3.Connection) -> None:
    columns = {row[1] for row in conn.execute("PRAGMA table_info(interactions)").fetchall()}
    new_cols = {
        "review_status": "TEXT DEFAULT 'auto_approved'",
        "draft_response": "TEXT",
        "human_edited_response": "TEXT",
        "reviewed_by": "TEXT",
        "reviewed_at": "TEXT",
    }
    for name, typedef in new_cols.items():
        if name not in columns:
            conn.execute(f"ALTER TABLE interactions ADD COLUMN {name} {typedef}")


def seed_from_csv(db_path: Path | None = None) -> None:
    init_schema(db_path)
    farmers_csv = DATA_DIR / "farmers.csv"
    if not farmers_csv.exists():
        return
    df = pd.read_csv(farmers_csv)
    with get_connection(db_path) as conn:
        existing = conn.execute("SELECT COUNT(*) FROM farmers").fetchone()[0]
        if existing > 0:
            return
        for _, row in df.iterrows():
            conn.execute(
                """INSERT INTO farmers
                (farmer_id, name, district, crop, land_acres, irrigation_type, language, crop_stage, phone)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    row["farmer_id"], row["name"], row["district"], row["crop"],
                    row["land_acres"], row["irrigation_type"], row["language"],
                    row["crop_stage"], row.get("phone", ""),
                ),
            )
        seed_interactions = DATA_DIR / "interactions_seed.csv"
        if seed_interactions.exists():
            idf = pd.read_csv(seed_interactions)
            for _, row in idf.iterrows():
                conn.execute(
                    """INSERT INTO interactions
                    (farmer_id, query_text, intent, language, confidence, escalated)
                    VALUES (?, ?, ?, ?, ?, ?)""",
                    (
                        row["farmer_id"], row["query"], row["intent"],
                        row["language"], row["confidence"], int(row["escalated"]),
                    ),
                )


def get_farmer(farmer_id: str) -> dict | None:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM farmers WHERE farmer_id = ?", (farmer_id,)).fetchone()
        return dict(row) if row else None


def list_farmers() -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM farmers ORDER BY name").fetchall()
        return [dict(r) for r in rows]


def upsert_farmer(data: dict) -> None:
    with get_connection() as conn:
        conn.execute(
            """INSERT INTO farmers
            (farmer_id, name, district, crop, land_acres, irrigation_type, language, crop_stage, phone)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(farmer_id) DO UPDATE SET
            name=excluded.name, district=excluded.district, crop=excluded.crop,
            land_acres=excluded.land_acres, irrigation_type=excluded.irrigation_type,
            language=excluded.language, crop_stage=excluded.crop_stage, phone=excluded.phone""",
            (
                data["farmer_id"], data["name"], data["district"], data["crop"],
                data.get("land_acres", 0), data.get("irrigation_type", "rainfed"),
                data.get("language", "english"), data.get("crop_stage", ""),
                data.get("phone", ""),
            ),
        )


def save_interaction(record: dict) -> int:
    with get_connection() as conn:
        cur = conn.execute(
            """INSERT INTO interactions
            (farmer_id, query_text, response_text, intent, language, confidence,
             escalated, agent_trace, citations, response_time_ms,
             review_status, draft_response, human_edited_response)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                record["farmer_id"], record["query_text"], record.get("response_text"),
                record.get("intent"), record.get("language"), record.get("confidence"),
                int(record.get("escalated", False)), json.dumps(record.get("agent_trace", {})),
                json.dumps(record.get("citations", [])), record.get("response_time_ms"),
                record.get("review_status", "auto_approved"),
                record.get("draft_response"),
                record.get("human_edited_response"),
            ),
        )
        return cur.lastrowid


def get_pending_reviews() -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            """SELECT i.*, f.name, f.district, f.crop
            FROM interactions i
            JOIN farmers f ON i.farmer_id = f.farmer_id
            WHERE i.review_status = 'pending_human'
            ORDER BY i.created_at DESC"""
        ).fetchall()
        return [dict(r) for r in rows]


def approve_interaction(interaction_id: int, edited_response: str, reviewer: str) -> None:
    with get_connection() as conn:
        conn.execute(
            """UPDATE interactions SET
            review_status = 'approved',
            response_text = ?,
            human_edited_response = ?,
            reviewed_by = ?,
            reviewed_at = datetime('now')
            WHERE interaction_id = ?""",
            (edited_response, edited_response, reviewer, interaction_id),
        )


def reject_interaction(interaction_id: int, reviewer: str, note: str = "") -> None:
    with get_connection() as conn:
        conn.execute(
            """UPDATE interactions SET
            review_status = 'rejected',
            response_text = ?,
            reviewed_by = ?,
            reviewed_at = datetime('now')
            WHERE interaction_id = ?""",
            (note or "Unable to provide guidance. A field officer will contact you.", reviewer, interaction_id),
        )


def get_interaction(interaction_id: int) -> dict | None:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM interactions WHERE interaction_id = ?", (interaction_id,)
        ).fetchone()
        return dict(row) if row else None


def get_interactions(farmer_id: str | None = None, limit: int = 50) -> list[dict]:
    with get_connection() as conn:
        if farmer_id:
            rows = conn.execute(
                "SELECT * FROM interactions WHERE farmer_id = ? ORDER BY created_at DESC LIMIT ?",
                (farmer_id, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM interactions ORDER BY created_at DESC LIMIT ?", (limit,)
            ).fetchall()
        return [dict(r) for r in rows]


def get_recent_interactions(farmer_id: str, limit: int = 5) -> list[dict]:
    return get_interactions(farmer_id, limit)


def create_case(case: dict) -> int:
    with get_connection() as conn:
        cur = conn.execute(
            """INSERT INTO cases
            (interaction_id, farmer_id, priority, status, assigned_role, summary)
            VALUES (?, ?, ?, ?, ?, ?)""",
            (
                case.get("interaction_id"), case["farmer_id"], case.get("priority", "medium"),
                case.get("status", "open"), case.get("assigned_role", "field_officer"),
                case.get("summary", ""),
            ),
        )
        return cur.lastrowid


def list_cases(status: str | None = None) -> list[dict]:
    with get_connection() as conn:
        if status:
            rows = conn.execute(
                "SELECT c.*, f.name, f.district, f.crop FROM cases c "
                "JOIN farmers f ON c.farmer_id = f.farmer_id WHERE c.status = ? ORDER BY c.created_at DESC",
                (status,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT c.*, f.name, f.district, f.crop FROM cases c "
                "JOIN farmers f ON c.farmer_id = f.farmer_id ORDER BY c.created_at DESC"
            ).fetchall()
        return [dict(r) for r in rows]


def update_case(case_id: int, **kwargs: Any) -> None:
    allowed = {"status", "follow_up_notes", "review_status", "assigned_role", "priority"}
    updates = {k: v for k, v in kwargs.items() if k in allowed and v is not None}
    if not updates:
        return
    updates["updated_at"] = datetime.utcnow().isoformat()
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    with get_connection() as conn:
        conn.execute(
            f"UPDATE cases SET {set_clause} WHERE case_id = ?",
            (*updates.values(), case_id),
        )


def save_audit_log(log: dict) -> None:
    with get_connection() as conn:
        conn.execute(
            """INSERT INTO audit_logs
            (interaction_id, user_role, action, model_used, chunk_ids, confidence,
             guardrail_triggered, details)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                log.get("interaction_id"), log.get("user_role"), log.get("action"),
                log.get("model_used"), json.dumps(log.get("chunk_ids", [])),
                log.get("confidence"), int(log.get("guardrail_triggered", False)),
                json.dumps(log.get("details", {})),
            ),
        )


def get_audit_logs(limit: int = 100) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM audit_logs ORDER BY created_at DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]


def save_outbreak_alert(alert: dict) -> int:
    with get_connection() as conn:
        cur = conn.execute(
            """INSERT INTO outbreak_alerts
            (district, crop, alert_type, query_count, message, status)
            VALUES (?, ?, ?, ?, ?, ?)""",
            (
                alert["district"], alert.get("crop"), alert.get("alert_type", "pest_cluster"),
                alert.get("query_count", 0), alert.get("message", ""),
                alert.get("status", "active"),
            ),
        )
        return cur.lastrowid


def get_outbreak_alerts(active_only: bool = True) -> list[dict]:
    with get_connection() as conn:
        if active_only:
            rows = conn.execute(
                "SELECT * FROM outbreak_alerts WHERE status = 'active' ORDER BY created_at DESC"
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM outbreak_alerts ORDER BY created_at DESC").fetchall()
        return [dict(r) for r in rows]


def get_kpis() -> dict:
    with get_connection() as conn:
        today = conn.execute(
            "SELECT COUNT(*) FROM interactions WHERE date(created_at) = date('now')"
        ).fetchone()[0]
        total = conn.execute("SELECT COUNT(*) FROM interactions").fetchone()[0]
        escalations = conn.execute(
            "SELECT COUNT(*) FROM cases WHERE status = 'open'"
        ).fetchone()[0]
        avg_ms = conn.execute(
            "SELECT AVG(response_time_ms) FROM interactions WHERE response_time_ms IS NOT NULL"
        ).fetchone()[0]
        pending = conn.execute(
            "SELECT COUNT(*) FROM interactions WHERE review_status = 'pending_human'"
        ).fetchone()[0]
        return {
            "queries_today": today,
            "total_queries": total,
            "open_escalations": escalations,
            "avg_response_ms": int(avg_ms or 0),
            "pending_hitl": pending,
        }


def get_farmer_kpis(farmer_id: str) -> dict:
    """KPIs scoped to one farmer account."""
    with get_connection() as conn:
        today = conn.execute(
            """SELECT COUNT(*) FROM interactions
            WHERE farmer_id = ? AND date(created_at) = date('now')""",
            (farmer_id,),
        ).fetchone()[0]
        total = conn.execute(
            "SELECT COUNT(*) FROM interactions WHERE farmer_id = ?", (farmer_id,)
        ).fetchone()[0]
        avg_ms = conn.execute(
            """SELECT AVG(response_time_ms) FROM interactions
            WHERE farmer_id = ? AND response_time_ms IS NOT NULL""",
            (farmer_id,),
        ).fetchone()[0]
        pending = conn.execute(
            """SELECT COUNT(*) FROM interactions
            WHERE farmer_id = ? AND review_status = 'pending_human'""",
            (farmer_id,),
        ).fetchone()[0]
        return {
            "queries_today": today,
            "total_queries": total,
            "avg_response_ms": int(avg_ms or 0),
            "pending_review": pending,
        }


def get_farmer_notification_summary(farmer_id: str) -> dict:
    """Pending reviews and recently expert-approved answers for in-app alerts."""
    with get_connection() as conn:
        pending_rows = conn.execute(
            """SELECT interaction_id, query_text, created_at FROM interactions
            WHERE farmer_id = ? AND review_status = 'pending_human'
            ORDER BY created_at DESC LIMIT 5""",
            (farmer_id,),
        ).fetchall()
        approved_rows = conn.execute(
            """SELECT interaction_id, query_text, reviewed_at FROM interactions
            WHERE farmer_id = ? AND review_status = 'approved'
            AND reviewed_at >= datetime('now', '-7 days')
            ORDER BY reviewed_at DESC LIMIT 5""",
            (farmer_id,),
        ).fetchall()
    return {
        "pending": [dict(r) for r in pending_rows],
        "recently_approved": [dict(r) for r in approved_rows],
        "pending_count": len(pending_rows),
    }


def count_pest_queries_by_district(days: int = 7) -> list[dict]:
    """Pest/disease interactions grouped by farmer profile district + crop."""
    with get_connection() as conn:
        rows = conn.execute(
            """SELECT f.district, f.crop,
                      COUNT(*) as cnt,
                      COUNT(DISTINCT i.farmer_id) as farmer_cnt
            FROM interactions i
            JOIN farmers f ON i.farmer_id = f.farmer_id
            WHERE i.intent = 'pest_disease'
            AND i.created_at >= datetime('now', ?)
            GROUP BY f.district, f.crop HAVING cnt >= 2""",
            (f"-{days} days",),
        ).fetchall()
        return [dict(r) for r in rows]


def resolve_outbreak_alert(alert_id: int) -> None:
    with get_connection() as conn:
        conn.execute(
            "UPDATE outbreak_alerts SET status = 'resolved' WHERE alert_id = ?",
            (alert_id,),
        )


def _ensure_dealer_requests(conn: sqlite3.Connection) -> None:
    conn.execute(
        """CREATE TABLE IF NOT EXISTS dealer_requests (
            request_id INTEGER PRIMARY KEY AUTOINCREMENT,
            farmer_id TEXT NOT NULL,
            district TEXT,
            crop TEXT,
            input_type TEXT,
            product_note TEXT,
            phone TEXT,
            status TEXT DEFAULT 'demo_logged',
            created_at TEXT DEFAULT (datetime('now'))
        )"""
    )


def save_dealer_request(
    farmer_id: str,
    district: str = "",
    crop: str = "",
    input_type: str = "",
    product_note: str = "",
    phone: str = "",
) -> int:
    init_schema()
    with get_connection() as conn:
        cur = conn.execute(
            """INSERT INTO dealer_requests
            (farmer_id, district, crop, input_type, product_note, phone)
            VALUES (?, ?, ?, ?, ?, ?)""",
            (farmer_id, district, crop, input_type, product_note, phone),
        )
        return int(cur.lastrowid)


def list_dealer_requests(farmer_id: str, limit: int = 10) -> list[dict]:
    init_schema()
    with get_connection() as conn:
        rows = conn.execute(
            """SELECT * FROM dealer_requests WHERE farmer_id = ?
            ORDER BY created_at DESC LIMIT ?""",
            (farmer_id, limit),
        ).fetchall()
    return [dict(r) for r in rows]


def reset_demo_data() -> None:
    if DB_PATH.exists():
        DB_PATH.unlink()
    seed_from_csv()
    from src.auth.users import init_users
    init_users(force=True)
