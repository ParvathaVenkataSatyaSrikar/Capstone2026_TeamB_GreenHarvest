"""Initialize SQLite database and seed from CSV."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.db.repository import init_schema, seed_from_csv
from src.auth.users import init_users
from config.settings import DB_PATH


def main():
    print(f"Initializing database at {DB_PATH}")
    init_schema()
    seed_from_csv()
    init_users()
    print("Database ready (farmers + demo users).")


if __name__ == "__main__":
    main()
