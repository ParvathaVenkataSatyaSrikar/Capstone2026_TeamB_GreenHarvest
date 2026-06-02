"""
Gemini embeddings via google.generativeai (lightweight — no langchain_google_genai).

Embeds each knowledge-base chunk individually for FAISS indexing.
"""
from __future__ import annotations

import json
import re
import time
import warnings
from datetime import date
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

from langchain_core.embeddings import Embeddings

from config.settings import DATA_DIR, get_settings

# Alternate model IDs (legacy text-embedding-* models are removed from the Gemini API)
EMBEDDING_MODEL_FALLBACKS = (
    "models/gemini-embedding-001",
    "gemini-embedding-001",
)

# Per-chunk timeout for slow networks; retried before failing a batch
EMBED_TIMEOUT_SEC = 120
EMBED_TIMEOUT_RETRIES = 4
EMBED_INTER_CHUNK_DELAY_SEC = 0.2

# Google AI free tier: ~1000 embed_content calls/day for gemini-embedding-001
GEMINI_EMBED_FREE_TIER_DAILY = 1000
QUOTA_PAUSE_PATH = DATA_DIR / "gemini_embed_quota_pause.json"


def record_daily_quota_pause() -> None:
    """Remember that today's free-tier embed quota was exhausted (skip API retries same day)."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    QUOTA_PAUSE_PATH.write_text(
        json.dumps({"date": date.today().isoformat()}),
        encoding="utf-8",
    )


def clear_daily_quota_pause() -> None:
    if QUOTA_PAUSE_PATH.exists():
        QUOTA_PAUSE_PATH.unlink()


def is_daily_quota_paused() -> bool:
    if not QUOTA_PAUSE_PATH.exists():
        return False
    try:
        data = json.loads(QUOTA_PAUSE_PATH.read_text(encoding="utf-8"))
        return data.get("date") == date.today().isoformat()
    except Exception:
        return False


class GeminiEmbeddingQuotaError(RuntimeError):
    """Gemini embed_content quota or rate limit — ingest should pause and resume later."""

    def __init__(
        self,
        message: str,
        *,
        daily_limit: bool = False,
        retry_after_sec: float | None = None,
    ):
        super().__init__(message)
        self.daily_limit = daily_limit
        self.retry_after_sec = retry_after_sec


def _load_genai():
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", FutureWarning)
            import google.generativeai as genai
        return genai
    except ImportError:
        return None


def embedding_available() -> bool:
    settings = get_settings()
    return bool(_load_genai() and settings.gemini_api_key)


class GeminiEmbeddingWrapper(Embeddings):
    """Per-chunk Gemini embeddings — compatible with FAISS.from_documents."""

    def __init__(self, api_key: str | None = None, model: str | None = None):
        settings = get_settings()
        self.api_key = api_key or settings.gemini_api_key
        self.model = model or settings.gemini_embedding_model
        self._genai = _load_genai()
        if self._genai and self.api_key:
            self._genai.configure(api_key=self.api_key)

    @staticmethod
    def _is_rate_limited(err: Exception) -> bool:
        msg = str(err).lower()
        return "429" in msg or "quota" in msg or "rate" in msg or "resource_exhausted" in msg

    @staticmethod
    def _is_daily_quota(err: Exception) -> bool:
        msg = str(err).lower().replace(" ", "")
        if "perday" in msg or "embedcontentrequestsperday" in msg:
            return True
        if "free_tier" in msg and "embed_content" in msg and "1000" in str(err):
            return True
        return "quota_value: 1000" in str(err) and "embed" in msg

    @staticmethod
    def _parse_retry_seconds(err: Exception) -> float | None:
        msg = str(err)
        match = re.search(r"retry in ([\d.]+)s", msg, re.IGNORECASE)
        if match:
            return float(match.group(1))
        match = re.search(r"retry_delay\s*\{[^}]*seconds:\s*(\d+)", msg, re.IGNORECASE | re.DOTALL)
        if match:
            return float(match.group(1))
        return None

    def _embed_one_sync(self, text: str, *, task_type: str = "RETRIEVAL_DOCUMENT") -> list[float]:
        if not self._genai or not self.api_key:
            raise RuntimeError("Gemini embedding not configured — set GEMINI_API_KEY in .env")

        safe = (text or " ").strip() or " "
        if len(safe) > 8000:
            safe = safe[:8000]

        models_to_try = [self.model] + [m for m in EMBEDDING_MODEL_FALLBACKS if m != self.model]
        errors: list[str] = []

        for model_name in models_to_try:
            for attempt in range(5):
                try:
                    result = self._genai.embed_content(
                        model=model_name,
                        content=safe,
                        task_type=task_type,
                    )
                    if hasattr(result, "embedding"):
                        return list(result.embedding)
                    if isinstance(result, dict) and "embedding" in result:
                        return list(result["embedding"])
                    errors.append(f"{model_name}: empty embedding response")
                except Exception as e:
                    errors.append(f"{model_name}: {e}")
                    if self._is_rate_limited(e):
                        if self._is_daily_quota(e):
                            record_daily_quota_pause()
                            raise GeminiEmbeddingQuotaError(
                                f"Gemini daily embedding quota reached "
                                f"(free tier ~{GEMINI_EMBED_FREE_TIER_DAILY}/day). "
                                "Re-run ingest_kb.py tomorrow to resume.",
                                daily_limit=True,
                            ) from e
                        retry_sec = self._parse_retry_seconds(e)
                        if retry_sec is not None and attempt < 4:
                            time.sleep(retry_sec + 2.0)
                            continue
                    if attempt < 4:
                        delay = 2.0 * (attempt + 1)
                        if self._is_rate_limited(e):
                            delay = min(60.0, 5.0 * (attempt + 1))
                        time.sleep(delay)
                    continue
                break

        detail = errors[-1] if errors else "unknown error"
        if errors and self._is_rate_limited(Exception(errors[-1])):
            if self._is_daily_quota(Exception(errors[-1])):
                raise GeminiEmbeddingQuotaError(
                    f"Gemini daily embedding quota reached "
                    f"(free tier ~{GEMINI_EMBED_FREE_TIER_DAILY}/day). "
                    "Re-run ingest_kb.py tomorrow to resume.",
                    daily_limit=True,
                )
        raise RuntimeError(
            "Gemini embedding failed. "
            f"Primary model: {self.model}. {detail}"
        )

    def _embed_one(self, text: str, *, task_type: str = "RETRIEVAL_DOCUMENT") -> list[float]:
        last_timeout: FuturesTimeoutError | None = None
        for attempt in range(EMBED_TIMEOUT_RETRIES):
            with ThreadPoolExecutor(max_workers=1) as pool:
                future = pool.submit(self._embed_one_sync, text, task_type=task_type)
                try:
                    return future.result(timeout=EMBED_TIMEOUT_SEC)
                except FuturesTimeoutError as exc:
                    last_timeout = exc
                    if attempt < EMBED_TIMEOUT_RETRIES - 1:
                        time.sleep(3.0 * (attempt + 1))
        raise RuntimeError(
            f"Gemini embedding timed out after {EMBED_TIMEOUT_RETRIES} tries "
            f"({EMBED_TIMEOUT_SEC}s each) — check network connectivity or retry ingest_kb.py"
        ) from last_timeout

    def embed_documents(self, texts: list[str], *, max_workers: int = 1) -> list[list[float]]:
        """Embed one chunk at a time (stable on slow networks; FAISS ingest uses this)."""
        if not texts:
            return []
        vectors: list[list[float]] = []
        for i, text in enumerate(texts):
            vectors.append(self._embed_one(text, task_type="RETRIEVAL_DOCUMENT"))
            if i < len(texts) - 1 and EMBED_INTER_CHUNK_DELAY_SEC > 0:
                time.sleep(EMBED_INTER_CHUNK_DELAY_SEC)
        return vectors

    def embed_query(self, text: str) -> list[float]:
        return self._embed_one(text, task_type="RETRIEVAL_QUERY")
