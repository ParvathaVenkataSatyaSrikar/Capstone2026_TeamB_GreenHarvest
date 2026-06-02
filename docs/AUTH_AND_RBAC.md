# Authentication and Role-Based Access Control

## Model

| Layer | Location | Behaviour |
|-------|----------|-----------|
| Login | `pages/0_Login.py` | Username and password per role |
| Session | `src/auth/session.py` | `auth_logged_in`, `auth_user`, `auth_role` |
| Users | `src/auth/users.py` | SQLite `users` table, SHA-256 password hashing |
| Permissions | `src/auth/rbac.py` | Page-to-permission-to-role mapping |
| UI enforcement | `src/ui/portal.py` | Sidebar displays only authorized pages |

## Demo accounts

| Username | Password | Role | Farmer ID |
|----------|----------|------|-----------|
| farmer_f001 | farmer123 | farmer | F001 |
| farmer_f002 | farmer123 | farmer | F002 |
| officer1 | officer2026 | field_officer | — |
| admin | admin2026 | admin | — |

Run `python scripts/init_db.py` then `python scripts/verify_auth.py` to validate credentials.

Field officers and administrators may also sign in with the optional `STAFF_DEMO_PASSWORD` value from `.env` (default documented in `.env.example`).

Home pages use distinct numeric prefixes (`10_`, `20_`, `30_`) to prevent Streamlit routing conflicts between portals.

## Page access matrix

| Page | Farmer | Field Officer | Admin |
|------|:------:|:-------------:|:-----:|
| Farmer Home / Advisor / My Queries | Yes | No | No |
| Officer Home / Review / Cases | No | Yes | Yes* |
| Admin Home / Analytics / Governance / KB / Settings | No | No | Yes |

\*Administrator has supervisor access to officer review and cases pages but cannot access Farmer AI Advisor.

## Session management

- **Logout** clears session state and redirects to the login page.
- Role cannot be changed without logout.
- Each account is bound to a single role.

## Developer notes

- Add users by inserting into the `users` table with `_hash_password()` from `users.py`.
- Register new pages in `PAGE_PERMISSIONS` and `ROLE_NAV` in `src/auth/rbac.py`.
- Call `require_permission()` at the top of each protected page.

See [DEVELOPMENT.md](DEVELOPMENT.md) for page registration procedure.
