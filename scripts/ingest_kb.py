"""Ingest knowledge base into FAISS with Gemini embeddings."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.rag.retriever import (
    ingest_knowledge_base,
    load_kb_documents,
    get_active_embedding_provider,
    get_ingest_status,
)


def main():
    from config.settings import get_settings
    from src.rag.gemini_embeddings import embedding_available

    def _scan_progress(done: int, total: int) -> None:
        print(f"  Scanning KB files {done}/{total}...", flush=True)

    print("  Loading knowledge base...", flush=True)
    docs = load_kb_documents(on_scan_progress=_scan_progress)
    print(f"Found {len(docs)} chunks from knowledge base")

    if not embedding_available():
        print("WARNING: GEMINI_API_KEY missing or google-generativeai not installed.")
        print("  pip install google-generativeai")
        print("  App will use keyword search until ingest succeeds.")
        return

    try:
        def _progress(done: int, total: int) -> None:
            pct = int(100 * done / total) if total else 0
            print(f"  Embedded {done}/{total} chunks ({pct}%)...", flush=True)

        status_before = get_ingest_status()
        if status_before.get("partial"):
            print(
                f"  Resuming partial ingest ({status_before['embedded']}/"
                f"{status_before['total']} chunks already on disk)...",
            )

        count = ingest_knowledge_base(on_progress=_progress)
        store = get_active_embedding_provider()
        status = get_ingest_status()

        if status.get("complete"):
            print(f"SUCCESS: Ingested {count} chunks into FAISS ({store}).")
        elif status.get("partial"):
            remaining = status["total"] - status["embedded"]
            print(
                f"PARTIAL: {status['embedded']}/{status['total']} chunks in FAISS. "
                "Re-run this script to continue (safe to retry anytime).",
            )
            print("  The app can use this partial index for semantic search on embedded chunks.")
            if remaining > 0:
                days = max(1, (remaining + 999) // 1000)
                print(
                    f"  Gemini free tier: ~1000 embeds/day — expect ~{days} more run(s) "
                    f"({remaining} chunks left). Run again tomorrow if you hit 429 quota.",
                )
        else:
            print(f"Done ({store}). FAISS index not created.")
            print("  Keyword search over all KB chunks still works.")
            print("  If you saw 429/quota or timeout errors, wait and retry ingest_kb.py later.")
    except KeyboardInterrupt:
        print("\nCancelled.")
        print("  Re-run to resume FAISS ingest. First run builds data/kb_chunks_cache.json (one-time).")
        raise SystemExit(1)
    except Exception as e:
        print(f"ERROR: {e}")
        print("  App still works with keyword search. Fix .env and retry.")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
