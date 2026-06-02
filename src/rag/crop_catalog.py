"""Crop catalog — detection, normalization, 80+ crops."""
from __future__ import annotations

CROP_NAMES: tuple[str, ...] = (
    "cotton", "wheat", "paddy", "rice", "tomato", "soybean", "maize", "corn",
    "sugarcane", "groundnut", "peanut", "chilli", "chili", "onion", "potato",
    "mustard", "sunflower", "bajra", "pearl millet", "jowar", "sorghum",
    "gram", "chickpea", "lentil", "moong", "urad", "arhar", "pigeon pea",
    "banana", "mango", "grapes", "apple", "citrus", "orange", "papaya",
    "brinjal", "eggplant", "cabbage", "cauliflower", "okra", "bhindi",
    "turmeric", "ginger", "coffee", "tea", "coconut", "arecanut",
    "barley", "oats", "ragi", "finger millet", "foxtail millet",
    "castor", "sesame", "til", "linseed", "flax", "niger",
    "watermelon", "muskmelon", "cucumber", "pumpkin", "bottle gourd",
    "bitter gourd", "ridge gourd", "sponge gourd", "drumstick", "moringa",
    "guava", "pomegranate", "sapota", "chiku", "lychee", "jackfruit",
    "pineapple", "strawberry", "blueberry", "pear", "plum", "peach",
    "tobacco", "mentha", "mint", "coriander", "cumin", "fennel",
    "fenugreek", "methi", "isabgol", "psyllium", "safflower", "niger seed",
    "berseem", "lucerne", "alfalfa", "hybrid napier", "marigold",
)

_ALIASES: dict[str, str] = {
    "rice": "paddy",
    "corn": "maize",
    "peanut": "groundnut",
    "chili": "chilli",
    "eggplant": "brinjal",
    "bhindi": "okra",
    "til": "sesame",
    "methi": "fenugreek",
    "chiku": "sapota",
    "finger millet": "ragi",
    "pearl millet": "bajra",
    "arhar": "pigeon pea",
    "gram": "chickpea",
    "green_gram": "moong",
    "black_gram": "urad",
}


def normalize_crop(name: str) -> str:
    n = (name or "").lower().strip().replace(" ", "_")
    return _ALIASES.get(n, n)


def detect_crop_in_text(text: str) -> str | None:
    """Return first crop mentioned in query (longest match first)."""
    lower = (text or "").lower()
    found: list[tuple[int, str]] = []
    for crop in sorted(CROP_NAMES, key=len, reverse=True):
        key = crop.replace("_", " ")
        if crop in lower or key in lower:
            found.append((len(crop), normalize_crop(crop)))
    if not found:
        return None
    found.sort(reverse=True)
    return found[0][1]


def crops_match(a: str, b: str) -> bool:
    if not a or not b:
        return True
    return normalize_crop(a) == normalize_crop(b)
