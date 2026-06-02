"""Tavily web search — used in context node for market/scheme/insurance intents (HITL lab style)."""
from config.settings import get_settings
from src.resilience.network import is_online


def tavily_available() -> bool:
    s = get_settings()
    return bool(s.tavily_api_key and is_online())


def _get_tavily_tool():
    from langchain_tavily import TavilySearch

    return TavilySearch(max_results=3)


def run_tavily_search(query: str, max_results: int = 3) -> list[dict]:
    """Invoke TavilySearch tool; return normalized snippets."""
    if not tavily_available():
        return []
    try:
        tool = _get_tavily_tool()
        raw = tool.invoke({"query": query})
        return _normalize_tavily_response(raw, max_results)
    except Exception:
        return _legacy_tavily_search(query, max_results)


def _normalize_tavily_response(raw, max_results: int) -> list[dict]:
    out: list[dict] = []
    if isinstance(raw, str):
        if raw.strip():
            out.append({"title": "Tavily", "content": raw[:800], "url": "", "source": "tavily"})
        return out

    if isinstance(raw, dict):
        if raw.get("answer"):
            out.append({
                "title": "Tavily summary",
                "content": str(raw["answer"])[:800],
                "url": "",
                "source": "tavily",
            })
        for item in raw.get("results", [])[:max_results]:
            out.append({
                "title": item.get("title", ""),
                "content": (item.get("content") or "")[:600],
                "url": item.get("url", ""),
                "source": "tavily",
            })
        return out

    if isinstance(raw, list):
        for item in raw[:max_results]:
            if isinstance(item, dict):
                out.append({
                    "title": item.get("title", "Web"),
                    "content": (item.get("content") or str(item))[:600],
                    "url": item.get("url", ""),
                    "source": "tavily",
                })
            elif isinstance(item, str):
                out.append({"title": "Web", "content": item[:600], "url": "", "source": "tavily"})
    return out


def _legacy_tavily_search(query: str, max_results: int) -> list[dict]:
    try:
        from tavily import TavilyClient

        client = TavilyClient(api_key=get_settings().tavily_api_key)
        resp = client.search(query=query, search_depth="basic", max_results=max_results, include_answer=True)
        return _normalize_tavily_response(resp, max_results)
    except Exception:
        return []


def search_web(query: str, max_results: int = 3) -> list[dict]:
    return run_tavily_search(query, max_results=max_results)


def format_for_context(snippets: list[dict]) -> str:
    if not snippets:
        return ""
    lines = []
    for s in snippets:
        lines.append(f"- {s.get('title', 'Web')}: {s.get('content', '')[:400]}")
    return "\n".join(lines)
