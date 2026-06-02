"""Full project smoke test — imports, auth, RBAC, pages, pipeline."""
import argparse
import os
import sys
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# Default to offline LLM for fast, reliable smoke checks without live API calls.
# Use: python scripts/smoke_test.py --live  (requires working API keys)
parser = argparse.ArgumentParser(description="GreenHarvest smoke test")
parser.add_argument(
    "--live",
    action="store_true",
    help="Run full pipeline with live OpenAI/Gemini APIs (slower; requires network and valid keys)",
)
args, _ = parser.parse_known_args()
if not args.live:
    os.environ["LLM_PROVIDER"] = "offline"

from config.settings import _load_env_file, get_settings

_load_env_file()
get_settings.cache_clear()

failed = []
PIPELINE_TIMEOUT_SEC = 120 if args.live else 45


def check(name: str, ok: bool, detail: str = ""):
    status = "PASS" if ok else "FAIL"
    print(f"{status}: {name}" + (f" — {detail}" if detail and not ok else ""))
    if not ok:
        failed.append(name)


def main():
    mode = "live API" if args.live else "offline (fast)"
    print(f"=== GreenHarvest Smoke Test [{mode}] ===\n")

    for rel in [
        "app.py", "pages/0_Login.py", "pages/10_Farmer_Home.py",
        "pages/20_Officer_Home.py", "pages/30_Admin_Home.py",
        "data/greenharvest.db", "requirements.txt",
    ]:
        check(f"file {rel}", (ROOT / rel).exists())

    for page in sorted((ROOT / "pages").glob("*.py")):
        try:
            compile(page.read_text(encoding="utf-8"), str(page), "exec")
            check(f"compile {page.name}", True)
        except SyntaxError as e:
            check(f"compile {page.name}", False, str(e))

    # Auth — import rbac/users before session (avoids ui package circular import)
    try:
        from src.auth.rbac import ROLE_HOME, page_allowed
        from src.auth.session import ROLE_META
        check("import auth.rbac", True)
        check("import auth.session ROLE_META", "admin" in ROLE_META)
        check("ROLE_HOME paths", ROLE_HOME["admin"] == "pages/30_Admin_Home.py")
    except Exception as e:
        check("import auth", False, str(e))
        page_allowed = lambda *_: False  # noqa: E731

    try:
        from src.auth.rbac import ROLE_META  # noqa: F401
        check("ROLE_META not in rbac", False, "should not export ROLE_META")
    except ImportError:
        check("ROLE_META not in rbac", True)

    from src.auth.users import authenticate, init_users

    try:
        init_users()
    except Exception as e:
        check("init_users", False, str(e))

    for u, p, r in [
        ("farmer_f001", "farmer123", "farmer"),
        ("officer1", "officer2026", "field_officer"),
        ("admin", "admin2026", "admin"),
        ("admin", "greenharvest2026", "admin"),
    ]:
        try:
            user = authenticate(u, p, expected_role=r)
            check(f"login {u}", user is not None and user["role"] == r)
        except Exception as e:
            check(f"login {u}", False, str(e))

    try:
        check("farmer blocked admin page", not page_allowed("farmer", "pages/30_Admin_Home.py"))
        check("admin allowed analytics", page_allowed("admin", "pages/6_Admin_Analytics.py"))
        check("farmer allowed advisor", page_allowed("farmer", "pages/2_Farmer_AI_Advisor.py"))
    except Exception as e:
        check("RBAC matrix", False, str(e))

    s = get_settings()
    run_pipeline = args.live and (s.gemini_api_key or s.openai_api_key)
    if not args.live:
        print("INFO: pipeline uses offline mode (add --live to test real APIs)\n")
        run_pipeline = True
    elif not (s.gemini_api_key or s.openai_api_key):
        print("SKIP: pipeline (no GEMINI/OPENAI API key; use offline mode)\n")
        run_pipeline = True
        os.environ["LLM_PROVIDER"] = "offline"
        get_settings.cache_clear()

    if run_pipeline:
        try:
            from src.services.support_service import run_support_query

            print(f"Running pipeline test (timeout {PIPELINE_TIMEOUT_SEC}s)...")
            with ThreadPoolExecutor(max_workers=1) as pool:
                future = pool.submit(
                    run_support_query,
                    "F001",
                    "cotton pest yellow leaves",
                    language="english",
                )
                result = future.result(timeout=PIPELINE_TIMEOUT_SEC)
            check("pipeline response", len(result.translated_response) > 30)
            check("pipeline intent", bool(result.intent))
        except FuturesTimeoutError:
            check(
                "pipeline",
                False,
                f"timed out after {PIPELINE_TIMEOUT_SEC}s — try without --live, or verify API keys and network",
            )
        except KeyboardInterrupt:
            check("pipeline", False, "interrupted — use default offline mode (no --live flag)")
        except Exception as e:
            check("pipeline", False, str(e))

    try:
        from src.rag.retriever import load_kb_documents

        check("knowledge docs", len(load_kb_documents()) > 0)
    except Exception as e:
        check("knowledge docs", False, str(e))

    try:
        from src.integrations.scheme_payment import get_mock_scheme_status
        from src.integrations.dealer_locator import find_dealers
        from src.db.repository import save_dealer_request, list_dealer_requests

        schemes = get_mock_scheme_status("F001", "Warangal")
        check("mock scheme status", len(schemes) >= 2 and schemes[0]["scheme"] == "PM-KISAN")
        dealers = find_dealers("Warangal", "pesticide")
        check("dealer locator", len(dealers) > 0)
        rid = save_dealer_request("F001", "Warangal", "cotton", "pesticide", "demo", "999")
        check("dealer request save", rid > 0)
        check("dealer request list", len(list_dealer_requests("F001")) > 0)
    except Exception as e:
        check("demo integrations", False, str(e))

    try:
        from src.graph.nodes import node_classify_intent

        out = node_classify_intent({"query": "cotton leaves yellow", "agent_trace": {}})
        check("intent classify sample", out.get("intent") == "pest_disease")
    except Exception as e:
        check("intent classify sample", False, str(e))

    print()
    if failed:
        print(f"FAILED ({len(failed)}): {', '.join(failed)}")
        sys.exit(1)
    print("All smoke tests passed.")
    if not args.live:
        print("Tip: run with --live once on a fast network to verify API keys.")
    sys.exit(0)


if __name__ == "__main__":
    main()
