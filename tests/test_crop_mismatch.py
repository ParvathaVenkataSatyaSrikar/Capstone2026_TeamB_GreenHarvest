"""Profile crop vs query crop handling."""
from src.rag.crop_mismatch import build_crop_mismatch_notice, get_effective_query_crop


def test_same_crop_no_mismatch():
    crop, mismatch = get_effective_query_crop("cotton", "bollworm on my cotton", {"crop": "cotton"})
    assert crop == "cotton"
    assert mismatch is None


def test_other_crop_detected_in_query():
    crop, mismatch = get_effective_query_crop("cotton", "how to control tomato leaf curl", {})
    assert crop == "tomato"
    assert mismatch == "tomato"


def test_mismatch_notice_english():
    note = build_crop_mismatch_notice("cotton", "tomato", "english")
    assert "profile" in note.lower() or "profile crop" in note.lower()
    assert "Tomato" in note
    assert "Cotton" in note
