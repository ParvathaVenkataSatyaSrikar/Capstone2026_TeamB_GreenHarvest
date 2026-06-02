"""Mock government scheme / payment status — demo only, not live treasury APIs."""
from __future__ import annotations

import hashlib
from datetime import date, timedelta
from typing import Any


def _seed(farmer_id: str) -> int:
    return int(hashlib.md5(farmer_id.encode("utf-8")).hexdigest()[:8], 16)


def get_mock_scheme_status(farmer_id: str, district: str = "") -> list[dict[str, Any]]:
    """Deterministic demo status per farmer (PM-KISAN + one state scheme)."""
    s = _seed(farmer_id)
    installment = (s % 3) + 1
    credited = (s % 5) != 0
    last = date.today() - timedelta(days=30 + (s % 45))
    next_d = last + timedelta(days=120)
    pm_status = "Credited to bank" if credited else "Pending — eKYC / bank update"
    state_name = "Telangana Rythu Bandhu" if "warangal" in (district or "").lower() else "State crop input subsidy"
    state_status = "Eligible — visit CSC" if (s % 2) else "Application under review"

    return [
        {
            "scheme": "PM-KISAN",
            "enrolled": True,
            "benefit": "₹6,000/year (3 installments of ₹2,000)",
            "installment": f"{installment} of 3",
            "last_payment": last.isoformat(),
            "next_expected": next_d.isoformat(),
            "status": pm_status,
            "reference": f"DEMO-PMK-{farmer_id[-4:].upper()}-{installment}",
            "note": "Demo data only. Check the real PM-KISAN portal with your Aadhaar-linked account.",
        },
        {
            "scheme": state_name,
            "enrolled": (s % 3) != 0,
            "benefit": "Input subsidy via licensed dealers (POS)",
            "installment": "—",
            "last_payment": "—",
            "next_expected": "—",
            "status": state_status,
            "reference": f"DEMO-STATE-{farmer_id[-4:].upper()}",
            "note": "No payment is processed inside GreenHarvest. This screen is for awareness only.",
        },
    ]
