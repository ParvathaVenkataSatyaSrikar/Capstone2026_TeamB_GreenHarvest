"""
GreenHarvest semantic color system.

Each token has a meaning — use the right color for the right UI job:
  crop_*     → fields, brand, farmer actions (growth)
  soil_*     → land profile, farm details, earth
  water_*    → weather, irrigation, sky context
  harvest_*  → schemes, benefits, mandi / rewards
  ai_*       → AI advisor, RAG, automated answers
  success_*  → approved, healthy, instant answers
  warning_*  → pending review, alerts, caution
  danger_*   → errors, rejection, urgent escalation
  info_*     → neutral information, links
  farmer/officer/admin → role identity in sidebar & nav
"""

GH: dict[str, str] = {
    # —— Crop & brand (primary green) ——
    "crop_primary": "#14532d",
    "crop_mid": "#166534",
    "crop_accent": "#22c55e",
    "crop_soft": "#4ade80",
    "crop_pale": "#dcfce7",
    "crop_mist": "#f0fdf4",
    # —— Soil & land ——
    "soil": "#92400e",
    "soil_mid": "#b45309",
    "soil_light": "#fffbeb",
    "soil_border": "#fcd34d",
    # —— Water & weather ——
    "water": "#0369a1",
    "water_mid": "#0284c7",
    "water_light": "#e0f2fe",
    "water_pale": "#f0f9ff",
    # —— Harvest & schemes ——
    "harvest": "#a16207",
    "harvest_mid": "#ca8a04",
    "harvest_light": "#fef9c3",
    # —— AI & knowledge ——
    "ai": "#0f766e",
    "ai_mid": "#14b8a6",
    "ai_light": "#ccfbf1",
    "ai_pale": "#f0fdfa",
    # —— Status ——
    "success": "#15803d",
    "success_bg": "#dcfce7",
    "success_border": "#86efac",
    "warning": "#c2410c",
    "warning_bg": "#ffedd5",
    "warning_border": "#fdba74",
    "danger": "#b91c1c",
    "danger_bg": "#fee2e2",
    "danger_border": "#fca5a5",
    "info": "#1d4ed8",
    "info_bg": "#dbeafe",
    "info_border": "#93c5fd",
    # —— Roles ——
    "farmer": "#166534",
    "farmer_light": "#22c55e",
    "officer": "#1e3a5f",
    "officer_light": "#3b82f6",
    "admin": "#6b21a8",
    "admin_light": "#a855f7",
    # —— Neutrals ——
    "text": "#1e293b",
    "text_soft": "#475569",
    "muted": "#64748b",
    "border": "#cbd5e1",
    "cream": "#faf8f5",
    "paper": "#ffffff",
    "shadow": "rgba(20, 83, 45, 0.12)",
    # Legacy aliases (keep imports working)
    "green_dark": "#14532d",
    "green_mid": "#166534",
    "green_light": "#22c55e",
    "green_pale": "#dcfce7",
    "gold": "#ca8a04",
}


def role_color(role: str) -> str:
    return {
        "farmer": GH["farmer"],
        "field_officer": GH["officer"],
        "admin": GH["admin"],
    }.get(role, GH["crop_mid"])


def css_root_variables() -> str:
    """Emit :root { } block for ENTERPRISE_CSS."""
    keys = [
        "crop_primary", "crop_mid", "crop_accent", "crop_soft", "crop_pale", "crop_mist",
        "soil", "soil_mid", "soil_light", "soil_border",
        "water", "water_mid", "water_light", "water_pale",
        "harvest", "harvest_mid", "harvest_light",
        "ai", "ai_mid", "ai_light", "ai_pale",
        "success", "success_bg", "success_border",
        "warning", "warning_bg", "warning_border",
        "danger", "danger_bg", "danger_border",
        "info", "info_bg", "info_border",
        "farmer", "farmer_light", "officer", "officer_light", "admin", "admin_light",
        "text", "text_soft", "muted", "border", "cream", "paper",
    ]
    lines = [f"        --gh-{k.replace('_', '-')}: {GH[k]};" for k in keys]
    lines.append(f"        --gh-shadow: {GH['shadow']};")
    lines.append("        --gh-radius: 16px;")
    # Short aliases used in older CSS
    lines.append(f"        --gh-dark: {GH['crop_primary']};")
    lines.append(f"        --gh-mid: {GH['crop_mid']};")
    lines.append(f"        --gh-light: {GH['crop_accent']};")
    lines.append(f"        --gh-pale: {GH['crop_pale']};")
    lines.append(f"        --gh-gold: {GH['harvest_mid']};")
    lines.append(f"        --gh-cream: {GH['cream']};")
    lines.append(f"        --gh-sky: {GH['water_light']};")
    lines.append(f"        --gh-text: {GH['text']};")
    lines.append(f"        --gh-muted: {GH['muted']};")
    lines.append(f"        --gh-border: {GH['success_border']};")
    return "\n".join(lines)
