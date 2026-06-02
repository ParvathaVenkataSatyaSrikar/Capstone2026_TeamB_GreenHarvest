"""Project readiness checklist."""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# Fast readiness check — uses offline LLM by default (no live API calls required)
os.environ.setdefault("LLM_PROVIDER", "offline")

checks = []
for p in ["app.py", "data/greenharvest.db", "src/graph/workflow.py", "src/services/support_service.py"]:
    checks.append((p, (ROOT / p).exists()))

from config.settings import get_settings
get_settings.cache_clear()
s = get_settings()
checks.append(("API key", bool(s.gemini_api_key)))

from src.graph.workflow import get_support_graph
graph = get_support_graph()
checks.append(("LangGraph compiles", graph is not None))

from src.services.support_service import run_support_query
result = run_support_query("F001", "cotton leaves turning yellow")
checks.append(("Pipeline response", len(result.translated_response) > 50))
checks.append(("No placeholder error", "Configure API" not in result.translated_response))
checks.append(("Intent detected", result.intent in ("pest_disease", "crop_advisory")))

from src.services.hitl_service import list_pending_for_review
checks.append(("HITL module", callable(list_pending_for_review)))

from src.auth.users import authenticate, init_users
init_users()
checks.append(("Admin login", authenticate("admin", "admin2026", "admin") is not None))
checks.append(("Alternate admin password", authenticate("admin", "greenharvest2026", "admin") is not None))

from src.auth.rbac import ROLE_HOME, page_allowed
checks.append(("Admin home RBAC", page_allowed("admin", ROLE_HOME["admin"])))
checks.append(("Farmer blocked admin", not page_allowed("farmer", ROLE_HOME["admin"])))

for page in (ROOT / "pages").glob("*.py"):
    try:
        compile(page.read_text(encoding="utf-8"), str(page), "exec")
        checks.append((f"compile {page.name}", True))
    except SyntaxError:
        checks.append((f"compile {page.name}", False))

# Test offline RAG (no API needed for retrieval)
from src.rag.retriever import retrieve, _keyword_retrieve
checks.append(("Offline keyword RAG", len(_keyword_retrieve("cotton pest", "cotton", 2)) > 0))

from src.resilience.llm_router import invoke_text
off = invoke_text("You are helpful.", "Say hello in one sentence.")
checks.append(("LLM invoke", bool(off.content and len(off.content.strip()) >= 3)))
print("=== Readiness ===\n")
for name, ok in checks:
    print(f"{'PASS' if ok else 'FAIL'}: {name}")
failed = [n for n, o in checks if not o]
print("\nREADY" if not failed else f"ISSUES: {failed}")
sys.exit(0 if not failed else 1)
