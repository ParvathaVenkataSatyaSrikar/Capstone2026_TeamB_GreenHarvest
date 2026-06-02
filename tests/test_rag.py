"""Test knowledge retrieval (FAISS or keyword)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.rag.retriever import load_kb_documents, retrieve, get_active_embedding_provider


def main():
    docs = load_kb_documents()
    print(f"KB chunks: {len(docs)}")
    print(f"Store: {get_active_embedding_provider()}")
    for q in ["cotton pest yellow leaves", "paddy irrigation kharif", "tomato fungal spot"]:
        hits = retrieve(q, top_k=2)
        print(f"\nQuery: {q}")
        for h in hits:
            src = h.get("metadata", {}).get("source", "?")
            print(f"  - {src} (score {h.get('score', 0)})")
    if len(docs) < 20:
        print("\nWARN: Run python scripts/expand_knowledge_base.py && ingest_kb.py")
    print("\nOK")
    sys.exit(0)


if __name__ == "__main__":
    main()
