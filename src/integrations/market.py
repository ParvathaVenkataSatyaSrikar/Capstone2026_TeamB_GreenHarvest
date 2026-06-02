"""Mock market price service — reads data/market_prices.csv (enriched schema)."""
from __future__ import annotations

import pandas as pd

from config.settings import DATA_DIR

_market_df: pd.DataFrame | None = None


def _normalize_df(df: pd.DataFrame) -> pd.DataFrame:
    """Support enrich_data_assets columns: market, modal_price_inr_quintal, …"""
    if df.empty:
        return df
    out = df.copy()
    if "district" not in out.columns and "market" in out.columns:
        out["district"] = out["market"].astype(str)
    if "mandi" not in out.columns:
        out["mandi"] = out["district"].astype(str)
    if "price_per_quintal_inr" not in out.columns:
        if "modal_price_inr_quintal" in out.columns:
            out["price_per_quintal_inr"] = pd.to_numeric(out["modal_price_inr_quintal"], errors="coerce")
        elif "modal_price" in out.columns:
            out["price_per_quintal_inr"] = pd.to_numeric(out["modal_price"], errors="coerce")
    if "prev_week_price" not in out.columns:
        if "min_price_inr_quintal" in out.columns:
            out["prev_week_price"] = pd.to_numeric(out["min_price_inr_quintal"], errors="coerce")
        else:
            out["prev_week_price"] = out["price_per_quintal_inr"] * 0.97
    if "trend" not in out.columns:
        out["trend"] = out.apply(
            lambda r: "up"
            if float(r["price_per_quintal_inr"]) > float(r["prev_week_price"])
            else ("down" if float(r["price_per_quintal_inr"]) < float(r["prev_week_price"]) else "stable"),
            axis=1,
        )
    out["crop"] = out["crop"].astype(str).str.lower()
    out["district"] = out["district"].astype(str)
    return out


def _load() -> pd.DataFrame:
    global _market_df
    if _market_df is None:
        path = DATA_DIR / "market_prices.csv"
        raw = pd.read_csv(path) if path.exists() else pd.DataFrame()
        _market_df = _normalize_df(raw)
    return _market_df


def get_market_price(district: str, crop: str) -> dict:
    df = _load()
    if df.empty:
        return {"message": "Market price data not loaded."}
    district = (district or "").strip()
    crop = (crop or "").strip().lower()
    row = df[
        (df["district"].str.lower() == district.lower()) & (df["crop"] == crop)
    ].head(1)
    if row.empty and district:
        row = df[df["district"].str.lower() == district.lower()].head(1)
    if row.empty and crop:
        row = df[df["crop"] == crop].head(1)
    if row.empty:
        return {"message": f"No mandi data for {crop or 'this crop'} in {district or 'your area'}."}
    r = row.iloc[0]
    price = float(r["price_per_quintal_inr"])
    prev = float(r.get("prev_week_price", price))
    trend = str(r.get("trend", "stable"))
    return {
        "district": str(r["district"]),
        "crop": str(r["crop"]),
        "mandi": str(r["mandi"]),
        "date": str(r.get("date", "latest")),
        "price_per_quintal_inr": price,
        "prev_week_price": prev,
        "trend": trend,
        "min_price_inr_quintal": float(r.get("min_price_inr_quintal", price - 200)),
        "max_price_inr_quintal": float(r.get("max_price_inr_quintal", price + 200)),
    }


def compare_nearby_mandis(crop: str) -> list[dict]:
    df = _load()
    if df.empty:
        return []
    crop = (crop or "").strip().lower()
    rows = df[df["crop"] == crop].head(8)
    return [
        {
            "district": str(r["district"]),
            "mandi": str(r["mandi"]),
            "price_per_quintal_inr": float(r["price_per_quintal_inr"]),
            "trend": str(r["trend"]),
        }
        for _, r in rows.iterrows()
    ]


def format_market_answer(district: str, crop: str, *, language: str = "english") -> str:
    """Farmer-friendly mandi price text (used in pipeline and backup mode)."""
    data = get_market_price(district, crop)
    if data.get("message"):
        return (
            f"**Market prices**\n\n{data['message']} "
            "Try naming your district in **My farm** profile for a closer mandi match."
        )
    price = data["price_per_quintal_inr"]
    prev = data.get("prev_week_price", price)
    change = price - prev
    direction = data.get("trend", "stable")
    arrow = {"up": "↑", "down": "↓", "stable": "→"}.get(direction, "→")
    lines = [
        f"**{data['crop'].title()} mandi price ({data['district']})**",
        f"- **Modal price:** ₹{price:,.0f} per quintal",
        f"- **Range today:** ₹{data.get('min_price_inr_quintal', price):,.0f} – "
        f"₹{data.get('max_price_inr_quintal', price):,.0f}",
        f"- **Vs last week:** {arrow} ₹{abs(change):,.0f} ({direction})",
        f"- **Mandi / market:** {data['mandi']}",
        f"- **Date (demo data):** {data.get('date', 'latest')}",
    ]
    others = compare_nearby_mandis(crop)
    if len(others) > 1:
        lines.append("\n**Other mandis (same crop):**")
        for o in others[:4]:
            if o["district"].lower() != data["district"].lower():
                lines.append(f"- {o['mandi']}: ₹{o['price_per_quintal_inr']:,.0f}/quintal")
    lines.append("\n*Demo mandi prices from GreenHarvest data — confirm at your local market before selling.*")
    return "\n".join(lines)
