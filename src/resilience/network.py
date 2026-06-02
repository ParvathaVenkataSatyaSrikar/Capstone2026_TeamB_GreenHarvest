"""Network and provider error helpers."""
import socket
import time
import urllib.error
import urllib.request

_CACHE_TTL_SEC = 90.0
_net_cache: dict | None = None


def _cache_get() -> bool | None:
    global _net_cache
    if _net_cache and (time.time() - _net_cache["t"]) < _CACHE_TTL_SEC:
        return _net_cache["v"]
    try:
        import streamlit as st

        entry = st.session_state.get("_gh_net_online")
        if entry and (time.time() - entry["t"]) < _CACHE_TTL_SEC:
            return entry["v"]
    except Exception:
        pass
    return None


def _cache_set(value: bool) -> None:
    global _net_cache
    now = time.time()
    _net_cache = {"v": value, "t": now}
    try:
        import streamlit as st

        st.session_state["_gh_net_online"] = {"v": value, "t": now}
    except Exception:
        pass


def is_online(timeout: float = 0.6) -> bool:
    """Best-effort internet check — cached ~90s; fast TCP probe only."""
    cached = _cache_get()
    if cached is not None:
        return cached
    online = False
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("8.8.8.8", 53))
        online = True
    except OSError:
        try:
            urllib.request.urlopen("https://www.google.com", timeout=timeout)
            online = True
        except (urllib.error.URLError, OSError, TimeoutError):
            online = False
    _cache_set(online)
    return online


def is_quota_or_auth_error(exc: Exception) -> bool:
    msg = str(exc).lower()
    markers = (
        "401", "403", "429", "quota", "insufficient", "invalid api key",
        "authentication", "permission", "billing", "exceeded", "rate limit",
        "unauthorized", "api key not valid", "resource_exhausted",
    )
    return any(m in msg for m in markers)


def is_retryable_provider_error(exc: Exception) -> bool:
    """Model not found, rate limits, or transient API errors — try next provider."""
    if is_quota_or_auth_error(exc):
        return True
    msg = str(exc).lower()
    markers = (
        "not_found", "404", "503", "502", "timeout",
        "connection error", "connectionerror", "temporarily unavailable",
    )
    return any(m in msg for m in markers)
