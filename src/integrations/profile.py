"""Farmer profile service."""
from src.db.repository import get_farmer, list_farmers, upsert_farmer


def get_profile(farmer_id: str) -> dict | None:
    return get_farmer(farmer_id)


def list_profiles() -> list[dict]:
    return list_farmers()


def save_profile(data: dict) -> None:
    upsert_farmer(data)
