"""Local image assets under assets/images/ (see IMAGE_FILES for filenames)."""
from __future__ import annotations

import base64
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
IMAGES_DIR = ROOT / "assets" / "images"

# Logical key → filename (jpg preferred; webp/png also checked)
IMAGE_FILES: dict[str, str] = {
    "hero_fields": "hero_fields.jpg",
    "hero_green": "hero_green.jpg",
    "login_farm": "login_farm.jpg",
    "wheat": "hero_wheat.jpg",
    "farmer": "card_farmer.jpg",
    "irrigation": "card_irrigation.jpg",
    "card_crop_guides": "card_crop_guides.jpg",
    "card_weather": "card_weather.jpg",
    "card_expert": "card_expert.jpg",
}

ALT_EXTENSIONS = (".webp", ".png", ".jpeg", ".JPG", ".WEBP", ".PNG")

AVATARS = {
    "farmer": "🧑‍🌾",
    "advisor": "🌱",
    "helper": "💡",
    "expert": "👨‍🌾",
}


def _resolve_file(key: str) -> Path | None:
    """Return path if image exists on disk."""
    name = IMAGE_FILES.get(key)
    if not name:
        return None
    base = IMAGES_DIR / Path(name).stem
    candidates = [IMAGES_DIR / name]
    for ext in ALT_EXTENSIONS:
        candidates.append(base.with_suffix(ext))
    for path in candidates:
        if path.is_file():
            return path
    return None


def image_exists(key: str) -> bool:
    return _resolve_file(key) is not None


def image_path(key: str) -> Path | None:
    """Filesystem path for st.image() — None if missing."""
    return _resolve_file(key)


@lru_cache(maxsize=24)
def image_data_uri(key: str) -> str | None:
    """Base64 data URI for HTML/CSS backgrounds — loaded lazily per key (not all at import)."""
    path = _resolve_file(key)
    if not path:
        return None
    suffix = path.suffix.lower()
    mime = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
    }.get(suffix, "image/jpeg")
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def image_url_for_css(key: str) -> str:
    """URL for inline CSS background-image; empty string if missing."""
    return image_data_uri(key) or ""


def list_missing_images() -> list[tuple[str, str]]:
    """Keys and expected filenames still needed."""
    missing = []
    for key, filename in IMAGE_FILES.items():
        if not image_exists(key):
            missing.append((key, filename))
    return missing


# Keys only — use image_url_for_css(key) to load one image at a time
IMAGES = IMAGE_FILES
