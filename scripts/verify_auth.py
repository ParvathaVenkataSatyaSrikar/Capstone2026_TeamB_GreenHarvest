"""Verify all demo logins and RBAC paths."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.auth.users import authenticate, init_users
from src.auth.rbac import ROLE_HOME, page_allowed

TESTS = [
    ("farmer_f001", "farmer123", "farmer"),
    ("officer1", "officer2026", "field_officer"),
    ("officer1", "greenharvest2026", "field_officer"),
    ("admin", "admin2026", "admin"),
    ("admin", "greenharvest2026", "admin"),
]

def main():
    init_users()
    failed = []
    for user, pwd, role in TESTS:
        r = authenticate(user, pwd, expected_role=role)
        ok = r is not None and r["role"] == role
        print(f"{'PASS' if ok else 'FAIL'}: {user} / {pwd} -> {role}")
        if not ok:
            failed.append((user, pwd, role))

    for role, home in ROLE_HOME.items():
        allowed = page_allowed(role, home)
        print(f"{'PASS' if allowed else 'FAIL'}: {role} home {home}")
        if not allowed:
            failed.append((role, "home", home))

    if failed:
        print("\nFAILED:", failed)
        sys.exit(1)
    print("\nAll auth checks passed.")
    sys.exit(0)


if __name__ == "__main__":
    main()
