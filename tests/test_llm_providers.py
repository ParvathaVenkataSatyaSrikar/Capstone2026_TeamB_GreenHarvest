"""Test OpenAI → Gemini → offline RAG chain."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from config.settings import get_settings
from src.resilience.llm_router import probe_providers, invoke_text

get_settings.cache_clear()


def main():
    print("=== LLM provider probe ===\n")
    status = probe_providers()
    for name, state in status.items():
        print(f"  {name}: {state}")

    print("\n=== Sample invoke ===\n")
    r = invoke_text(
        "You are a brief agriculture assistant.",
        "In one sentence: when should I irrigate cotton?",
    )
    print(f"  provider: {r.provider}")
    print(f"  offline: {r.offline}")
    print(f"  preview: {r.content[:200]}...")

    failed = [k for k, v in status.items() if v in ("error", "timeout") and k != "network"]
    if failed and r.offline:
        print("\nWARN: All online providers failed; offline RAG used (expected if no keys).")
    elif not r.content:
        print("\nFAIL: empty response")
        sys.exit(1)
    print("\nOK")
    sys.exit(0)


if __name__ == "__main__":
    main()
