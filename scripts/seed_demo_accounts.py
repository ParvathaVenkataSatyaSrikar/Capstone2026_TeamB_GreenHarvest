"""Seed 25 demo farmers, 5 field officers, and sample interactions for analytics."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from config.settings import DB_PATH
from src.db.repository import init_schema, get_connection
from src.auth.demo_seed import DEMO_FARMERS, DEMO_OFFICERS, ensure_demo_farmers_and_officers


def main():
    print(f"Database: {DB_PATH}")
    init_schema()
    import src.auth.demo_seed as ds
    ds._demo_accounts_seeded = False
    stats = ensure_demo_farmers_and_officers(seed_interactions=True)

    with get_connection() as conn:
        n_farmers = conn.execute("SELECT COUNT(*) FROM farmers").fetchone()[0]
        n_users = conn.execute("SELECT COUNT(*) FROM users WHERE role='farmer'").fetchone()[0]
        n_officers = conn.execute("SELECT COUNT(*) FROM users WHERE role='field_officer'").fetchone()[0]
        n_ix = conn.execute("SELECT COUNT(*) FROM interactions").fetchone()[0]

    print(f"Demo farmers defined: {len(DEMO_FARMERS)}")
    print(f"Demo officers defined: {len(DEMO_OFFICERS)}")
    print(f"Stats: {stats}")
    print(f"In DB — farmers: {n_farmers}, farmer logins: {n_users}, officers: {n_officers}, interactions: {n_ix}")
    print("\nFarmer login: farmer_f001 .. farmer_f025  |  password: farmer123")
    print("Officer login: officer1 .. officer5       |  password: officer2026")


if __name__ == "__main__":
    main()
