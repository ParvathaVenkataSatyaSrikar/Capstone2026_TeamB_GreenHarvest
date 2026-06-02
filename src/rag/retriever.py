"""
Knowledge retrieval — FAISS vector search with Gemini embeddings.

Pipeline:
  load markdown → chunk → embed → FAISS → retrieve by query
Keyword fallback when no GEMINI_API_KEY or index is missing.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from config.settings import DATA_DIR, FAISS_DIR, KB_DIR, get_settings

_faiss_store: FAISS | None = None
_active_store: str = "keyword"
_kb_docs_cache: list[dict] | None = None


def get_active_embedding_provider() -> str:
    return _active_store


def get_embedding_model():
    """Gemini embedding wrapper for FAISS RAG."""
    from src.rag.gemini_embeddings import GeminiEmbeddingWrapper, embedding_available

    if not embedding_available():
        return None
    try:
        return GeminiEmbeddingWrapper()
    except Exception:
        return None


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 80) -> list[str]:
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = " ".join(words[i : i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)
        i += chunk_size - overlap
    return chunks or [text]


KB_CHUNKS_CACHE_PATH = DATA_DIR / "kb_chunks_cache.json"


def _kb_fingerprint() -> str:
    """Fast KB change detector (file count + newest mtime) — no full file reads."""
    count = 0
    newest = 0.0
    for path in KB_DIR.rglob("*.md"):
        count += 1
        try:
            newest = max(newest, path.stat().st_mtime)
        except OSError:
            pass
    return f"{count}:{newest:.0f}"


def _chunk_count_from_cache_file() -> int:
    if not KB_CHUNKS_CACHE_PATH.exists():
        return 0
    try:
        cached = json.loads(KB_CHUNKS_CACHE_PATH.read_text(encoding="utf-8"))
        return len(cached.get("docs", []))
    except Exception:
        return 0


def _build_kb_documents_from_disk(*, on_scan_progress=None) -> list[dict]:
    paths = sorted(KB_DIR.rglob("*.md"))
    total_files = len(paths)
    docs: list[dict] = []
    for file_idx, path in enumerate(paths):
        content = path.read_text(encoding="utf-8")
        rel = path.relative_to(KB_DIR)
        parts = rel.parts
        category = parts[0] if parts else "general"
        crop = ""
        stem = Path(parts[-1]).stem if parts else ""
        if category == "crops" and len(parts) > 1:
            crop = stem
        elif "_" in stem:
            crop = stem.split("_")[0]
        if not crop:
            for line in content.splitlines()[:12]:
                if line.strip().lower().startswith("crop:"):
                    crop = line.split(":", 1)[1].strip().lower()
                    break
        for idx, chunk in enumerate(chunk_text(content)):
            docs.append({
                "id": f"{rel.as_posix().replace('/', '_')}_{idx}",
                "text": chunk,
                "metadata": {
                    "source": str(rel),
                    "category": category,
                    "crop": crop,
                },
            })
        if on_scan_progress and total_files and (file_idx + 1) % 400 == 0:
            on_scan_progress(file_idx + 1, total_files)
    return docs


def load_kb_documents(*, force_reload: bool = False, on_scan_progress=None) -> list[dict]:
    """Load chunked KB docs; uses disk cache when knowledge_base/ is unchanged."""
    global _kb_docs_cache
    if _kb_docs_cache is not None and not force_reload:
        return _kb_docs_cache

    fingerprint = _kb_fingerprint()
    cache_path = KB_CHUNKS_CACHE_PATH

    if not force_reload and cache_path.exists():
        try:
            cached = json.loads(cache_path.read_text(encoding="utf-8"))
            if cached.get("fingerprint") == fingerprint and cached.get("docs"):
                _kb_docs_cache = cached["docs"]
                return _kb_docs_cache
        except Exception:
            pass

    docs = _build_kb_documents_from_disk(on_scan_progress=on_scan_progress)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(
        json.dumps({"fingerprint": fingerprint, "docs": docs}, ensure_ascii=False),
        encoding="utf-8",
    )
    _kb_docs_cache = docs
    return docs


def _tokenize(text: str) -> set[str]:
    words = set(re.findall(r"\w+", text.lower()))
    expanded: set[str] = set()
    for w in words:
        expanded.add(w)
        if len(w) > 4:
            expanded.add(w[:5])
    return expanded


def _keyword_retrieve(query: str, crop: str = "", top_k: int = 4) -> list[dict]:
    docs = load_kb_documents()
    if not docs:
        return []
    query_words = _tokenize(query)
    crop_l = crop.lower().strip()
    if crop_l:
        crop_docs = [d for d in docs if d["metadata"].get("crop", "").lower() == crop_l]
        if crop_docs:
            docs = crop_docs
    scored = []
    for doc in docs:
        text_words = _tokenize(doc["text"])
        overlap = len(query_words & text_words)
        if overlap > 0:
            scored.append({**doc, "score": round(min(0.95, 0.4 + overlap * 0.08), 3)})
    scored.sort(key=lambda x: x["score"], reverse=True)
    if not scored and query_words:
        for doc in docs[:top_k]:
            scored.append({**doc, "score": 0.35})
    return scored[:top_k]


def _docs_to_langchain(docs: list[dict]) -> list[Document]:
    return [
        Document(
            page_content=d["text"],
            metadata=dict(d["metadata"]),
            id=d["id"],
        )
        for d in docs
    ]


def _faiss_index_path() -> Path:
    return FAISS_DIR / "index.faiss"


def _ingest_progress_path() -> Path:
    return FAISS_DIR / "ingest_progress.json"


def _read_ingest_progress() -> int:
    path = _ingest_progress_path()
    if not path.exists():
        return 0
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return int(data.get("embedded", 0))
    except Exception:
        return 0


def _write_ingest_progress(embedded: int) -> None:
    FAISS_DIR.mkdir(parents=True, exist_ok=True)
    _ingest_progress_path().write_text(
        json.dumps({"embedded": embedded}),
        encoding="utf-8",
    )


def _clear_ingest_progress() -> None:
    path = _ingest_progress_path()
    if path.exists():
        path.unlink()


def get_ingest_status() -> dict:
    """How far KB → FAISS ingest has progressed (for scripts and admin UI)."""
    total = _chunk_count_from_cache_file() or len(load_kb_documents())
    embedded = _read_ingest_progress()
    has_index = _faiss_index_path().exists()
    if has_index and embedded == 0:
        return {
            "embedded": total,
            "total": total,
            "complete": total > 0,
            "partial": False,
            "has_index": True,
        }
    if embedded > 0 and has_index:
        return {
            "embedded": embedded,
            "total": total,
            "complete": False,
            "partial": True,
            "has_index": True,
        }
    return {
        "embedded": 0,
        "total": total,
        "complete": False,
        "partial": False,
        "has_index": has_index,
    }


def _load_faiss() -> FAISS | None:
    global _faiss_store, _active_store
    if _faiss_store is not None:
        return _faiss_store
    if not _faiss_index_path().exists():
        return None
    emb = get_embedding_model()
    if emb is None:
        return None
    try:
        _faiss_store = FAISS.load_local(
            str(FAISS_DIR),
            emb,
            allow_dangerous_deserialization=True,
        )
        _active_store = "faiss_gemini"
        return _faiss_store
    except Exception:
        return None


def ingest_knowledge_base(batch_size: int = 10, on_progress=None) -> int:
    """Build FAISS index from knowledge_base/ in batches (avoids single huge embed call)."""
    global _faiss_store, _active_store

    docs = load_kb_documents()
    if not docs:
        return 0

    emb = get_embedding_model()
    if emb is None:
        _active_store = "keyword"
        return len(docs)

    total = len(docs)
    FAISS_DIR.mkdir(parents=True, exist_ok=True)

    resume_from = 0
    if _faiss_index_path().exists():
        resume_from = _read_ingest_progress()
        if 0 < resume_from < total:
            try:
                _faiss_store = FAISS.load_local(
                    str(FAISS_DIR),
                    emb,
                    allow_dangerous_deserialization=True,
                )
                if on_progress:
                    print(f"  Resuming from chunk {resume_from}/{total}...", flush=True)
            except Exception:
                resume_from = 0
                _faiss_store = None
        else:
            resume_from = 0
            _faiss_store = None
    else:
        _faiss_store = None

    from src.rag.gemini_embeddings import (
        GEMINI_EMBED_FREE_TIER_DAILY,
        GeminiEmbeddingQuotaError,
        is_daily_quota_paused,
        record_daily_quota_pause,
        clear_daily_quota_pause,
    )

    if is_daily_quota_paused() and resume_from < total:
        saved = resume_from or _read_ingest_progress()
        if saved and _faiss_index_path().exists():
            try:
                _faiss_store = FAISS.load_local(
                    str(FAISS_DIR),
                    emb,
                    allow_dangerous_deserialization=True,
                )
                _active_store = "faiss_gemini"
            except Exception:
                _faiss_store = None
                _active_store = "keyword"
        if on_progress:
            remaining = total - saved
            days = max(1, (remaining + GEMINI_EMBED_FREE_TIER_DAILY - 1) // GEMINI_EMBED_FREE_TIER_DAILY)
            print(
                "  Skipping embed API calls — daily quota was already reached today.",
                flush=True,
            )
            print(
                f"  Progress unchanged at {saved}/{total}. "
                f"Run again tomorrow (~{days} day(s) left for ~{remaining} chunks).",
                flush=True,
            )
        return len(docs)

    try:
        for start in range(resume_from, total, batch_size):
            batch = docs[start : start + batch_size]
            lc_batch = _docs_to_langchain(batch)
            if _faiss_store is None:
                _faiss_store = FAISS.from_documents(lc_batch, emb)
            else:
                _faiss_store.add_documents(lc_batch)
            done = min(start + len(batch), total)
            _faiss_store.save_local(str(FAISS_DIR))
            _write_ingest_progress(done)
            if on_progress:
                on_progress(done, total)
        if _faiss_store is not None:
            _active_store = "faiss_gemini"
            _clear_ingest_progress()
            clear_daily_quota_pause()
    except Exception as exc:
        saved = _read_ingest_progress()
        if saved and _faiss_index_path().exists():
            try:
                _faiss_store = FAISS.load_local(
                    str(FAISS_DIR),
                    emb,
                    allow_dangerous_deserialization=True,
                )
                _active_store = "faiss_gemini"
            except Exception:
                _faiss_store = None
                _active_store = "keyword"
        else:
            _faiss_store = None
            _active_store = "keyword"
        if on_progress:
            if isinstance(exc, GeminiEmbeddingQuotaError) and exc.daily_limit:
                record_daily_quota_pause()
                print(f"  {exc}", flush=True)
                remaining = total - saved
                days = max(1, (remaining + GEMINI_EMBED_FREE_TIER_DAILY - 1) // GEMINI_EMBED_FREE_TIER_DAILY)
                print(
                    f"  Free tier allows ~{GEMINI_EMBED_FREE_TIER_DAILY} embeds/day — "
                    f"about {days} more day(s) to finish (~{remaining} chunks left).",
                    flush=True,
                )
            else:
                print(f"  Ingest error: {exc}", flush=True)
            if saved:
                print(
                    f"  Partial index saved ({saved}/{total} chunks). "
                    "Re-run ingest_kb.py to resume.",
                    flush=True,
                )
        return len(docs)

    return len(docs)


def _docs_to_chunks(docs: list, settings) -> list[dict]:
    chunks = []
    for doc in docs:
        meta = doc.metadata if hasattr(doc, "metadata") else {}
        chunks.append({
            "id": meta.get("source", ""),
            "text": doc.page_content,
            "metadata": meta,
            "score": round(max(settings.retrieval_min_score, 0.55), 3),
        })
    return chunks


def retrieve(query: str, crop: str = "", top_k: int = 4) -> list[dict]:
    settings = get_settings()

    store = _load_faiss()
    if store is None and not _faiss_index_path().exists():
        try:
            ingest_knowledge_base()
        except Exception:
            pass
        store = _load_faiss()

    if store is not None:
        try:
            retriever = store.as_retriever(search_kwargs={"k": top_k})
            results = retriever.invoke(query)
            chunks = _docs_to_chunks(results, settings)
            if crop:
                crop_l = crop.lower()
                filtered = [c for c in chunks if c["metadata"].get("crop", "").lower() == crop_l]
                if filtered:
                    chunks = filtered
                elif len(chunks) < top_k:
                    extra = _keyword_retrieve(query, crop, top_k)
                    chunks = (filtered or extra)[:top_k]
            if chunks:
                return chunks[:top_k]
        except Exception:
            pass

    return _keyword_retrieve(query, crop, top_k)
