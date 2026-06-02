"""Analytics and outbreak detection."""
import pandas as pd
from src.db.repository import (
    count_pest_queries_by_district,
    get_outbreak_alerts,
    save_outbreak_alert,
    get_connection,
)

# Demo-friendly threshold — raise in production (e.g. 5+ queries, 3+ farmers).
PEST_QUERY_THRESHOLD = 2


def check_outbreak_patterns() -> list[dict]:
    clusters = count_pest_queries_by_district(days=7)
    new_alerts = []
    existing = {(a["district"], a.get("crop", "")) for a in get_outbreak_alerts(active_only=True)}
    for row in clusters:
        district = row["district"]
        crop = row.get("crop", "")
        cnt = int(row["cnt"])
        farmer_cnt = int(row.get("farmer_cnt") or 0)
        if cnt >= PEST_QUERY_THRESHOLD and (district, crop) not in existing:
            farmer_note = (
                f"{farmer_cnt} farmer(s)"
                if farmer_cnt != 1
                else "1 farmer (multiple questions — verify in field)"
            )
            msg = (
                f"Possible pest cluster: {cnt} pest/disease queries from {farmer_note} "
                f"in {district} for {crop} in the last 7 days. Officer verification recommended."
            )
            alert_id = save_outbreak_alert({
                "district": district,
                "crop": crop,
                "alert_type": "pest_cluster",
                "query_count": cnt,
                "message": msg,
            })
            new_alerts.append({"alert_id": alert_id, "district": district, "message": msg})
    return new_alerts


def get_intent_distribution() -> pd.DataFrame:
    with get_connection() as conn:
        df = pd.read_sql_query(
            "SELECT intent, COUNT(*) as count FROM interactions WHERE intent IS NOT NULL GROUP BY intent",
            conn,
        )
    return df


def get_district_activity() -> pd.DataFrame:
    with get_connection() as conn:
        return pd.read_sql_query(
            """SELECT f.district, i.intent, COUNT(*) as count
            FROM interactions i JOIN farmers f ON i.farmer_id = f.farmer_id
            GROUP BY f.district, i.intent""",
            conn,
        )


def get_escalation_rate() -> float:
    with get_connection() as conn:
        total = conn.execute("SELECT COUNT(*) FROM interactions").fetchone()[0]
        esc = conn.execute("SELECT COUNT(*) FROM interactions WHERE escalated = 1").fetchone()[0]
    if total == 0:
        return 0.0
    return round(esc / total * 100, 1)


def get_confidence_series() -> pd.DataFrame:
    with get_connection() as conn:
        return pd.read_sql_query(
            "SELECT confidence, created_at FROM interactions WHERE confidence IS NOT NULL ORDER BY created_at",
            conn,
        )
