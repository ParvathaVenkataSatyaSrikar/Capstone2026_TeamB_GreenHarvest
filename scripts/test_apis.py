"""Quick API health check — OpenAI, Gemini, RAG, optional Tavily."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from config.settings import get_settings

get_settings.cache_clear()
s = get_settings()

print("=== API keys (set/missing) ===")
print(f"  OPENAI_API_KEY: {'set' if s.openai_api_key else 'MISSING'}")
print(f"  GEMINI_API_KEY: {'set' if s.gemini_api_key else 'MISSING'}")
print(f"  TAVILY_API_KEY: {'set' if s.tavily_api_key else 'optional'}")

from src.resilience.llm_router import probe_providers
print("\n=== LLM probe ===")
for k, v in probe_providers().items():
    print(f"  {k}: {v}")

from src.rag.retriever import load_kb_documents, get_active_embedding_provider
print(f"\n=== RAG ===\n  chunks: {len(load_kb_documents())}\n  store: {get_active_embedding_provider()}")

if s.tavily_api_key:
    from src.integrations.tavily_search import tavily_available, search_web
    print(f"\n=== Tavily ===\n  active: {tavily_available()}")
    if tavily_available():
        print(f"  sample: {search_web('cotton mandi India', max_results=1)}")

print("\nDone. Run: python tests/test_vision.py")
