# Development Guide

## Module map

```
app.py                 → Redirect to login or role home
pages/0_Login.py       → Authentication entry
pages/10_*.py          → Farmer portal
pages/20_*.py          → Field officer portal
pages/30_*.py          → Administrator portal

src/auth/              → Users, session, RBAC
src/graph/             → LangGraph crop advisory pipeline
src/services/          → support_service, hitl_service
src/helper/            → Portal Assistant (application help)
src/ui/portal.py       → Authenticated sidebar and navigation
```

## AI components

| Component | Purpose | Entry point |
|-----------|---------|-------------|
| AI Crop Advisor | Crop, pest, scheme, and market queries | `run_support_query()` in `src/services/support_service.py` |
| Portal Assistant | Application navigation and workflow help | `src/helper/assistant.py` |

These systems are intentionally separated. Portal Assistant does not invoke the crop advisory pipeline.

## Adding a new page

1. Create `pages/N_Role_Feature.py` following existing page conventions.
2. Register the page in `src/auth/rbac.py`:
   - Add to `PAGE_PERMISSIONS`
   - Add to `ROLE_NAV[role]`
3. At the top of the page:

```python
from src.auth.rbac import require_permission
from src.ui.portal import render_role_sidebar

require_permission("pages/N_Role_Feature.py")
role, language = render_role_sidebar("Feature Name")
```

## Extending the LangGraph pipeline

1. Add fields to `src/graph/state.py` if new state is required.
2. Implement node function in `src/graph/nodes.py`.
3. Register the node in `src/graph/workflow.py`.
4. Add unit or smoke test coverage where applicable.

## Adding integration data

1. Add CSV file under `data/`.
2. Implement fetch function in `src/integrations/`.
3. Route the intent in `src/graph/nodes.py` (`_integration_recommendation` or context builder).

## Local development workflow

```powershell
python scripts/init_db.py
python scripts/verify_auth.py
python scripts/ingest_kb.py
streamlit run app.py
```

After code changes to the knowledge base:

```powershell
python scripts/ingest_kb.py
python scripts/smoke_test.py
```

## Testing

| Command | Purpose |
|---------|---------|
| `python scripts/smoke_test.py` | End-to-end health check |
| `python scripts/eval_intent_classification.py` | Intent classification accuracy |
| `python -m pytest tests/` | Unit tests |

## Code conventions

- Match existing naming and import style in surrounding modules.
- Keep UI logic in `pages/` and `src/ui/`; business logic in `src/services/` and `src/graph/`.
- Use Pydantic schemas in `src/chains/schemas.py` for structured LLM output.
- Log governance events via `src/governance/audit.py`.

## Related documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) — system design
- [AUTH_AND_RBAC.md](AUTH_AND_RBAC.md) — security model
- [USER_STORIES.md](USER_STORIES.md) — functional requirements
