"""Role-based access control — permissions matrix."""

PERMISSIONS = {
    "farmer.home": ("farmer",),
    "farmer.advisor": ("farmer",),
    "farmer.history": ("farmer",),
    "officer.home": ("field_officer",),
    "officer.review": ("field_officer", "admin"),
    "officer.cases": ("field_officer", "admin"),
    "admin.analytics": ("admin",),
    "admin.governance": ("admin",),
    "admin.knowledge": ("admin",),
    "admin.home": ("admin",),
    "admin.settings": ("admin",),
    "helper.chat": ("farmer", "field_officer", "admin"),
}

PAGE_PERMISSIONS = {
    "pages/10_Farmer_Home.py": "farmer.home",
    "pages/20_Officer_Home.py": "officer.home",
    "pages/30_Admin_Home.py": "admin.home",
    "pages/2_Farmer_AI_Advisor.py": "farmer.advisor",
    "pages/3_Farmer_My_Queries.py": "farmer.history",
    "pages/4_Officer_Human_Review.py": "officer.review",
    "pages/5_Officer_Field_Cases.py": "officer.cases",
    "pages/6_Admin_Analytics.py": "admin.analytics",
    "pages/7_Admin_Governance.py": "admin.governance",
    "pages/8_Admin_Knowledge.py": "admin.knowledge",
    "pages/9_Admin_Settings.py": "admin.settings",
}

ROLE_HOME = {
    "farmer": "pages/10_Farmer_Home.py",
    "field_officer": "pages/20_Officer_Home.py",
    "admin": "pages/30_Admin_Home.py",
}

ROLE_NAV = {
    "farmer": [
        ("pages/10_Farmer_Home.py", "Home", "🏠"),
        ("pages/2_Farmer_AI_Advisor.py", "AI Crop Advisor", "💬"),
        ("pages/3_Farmer_My_Queries.py", "My Queries", "📋"),
    ],
    "field_officer": [
        ("pages/20_Officer_Home.py", "Home", "🏠"),
        ("pages/4_Officer_Human_Review.py", "Human Review", "✅"),
        ("pages/5_Officer_Field_Cases.py", "Field Cases", "📁"),
    ],
    "admin": [
        ("pages/30_Admin_Home.py", "Home", "🏠"),
        ("pages/6_Admin_Analytics.py", "Analytics", "📈"),
        ("pages/4_Officer_Human_Review.py", "Human Review", "✅"),
        ("pages/5_Officer_Field_Cases.py", "Cases", "📁"),
        ("pages/7_Admin_Governance.py", "Governance", "🛡️"),
        ("pages/8_Admin_Knowledge.py", "Knowledge", "📚"),
        ("pages/9_Admin_Settings.py", "Settings", "⚙️"),
    ],
}


def role_has_permission(role: str, permission: str) -> bool:
    return role in PERMISSIONS.get(permission, ())


def page_allowed(role: str, page_path: str) -> bool:
    perm = PAGE_PERMISSIONS.get(page_path.replace("\\", "/"))
    if not perm:
        return True
    return role_has_permission(role, perm)
