"""LLM routing: OpenAI → Gemini → offline RAG (fast models, timeouts)."""
from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from typing import Any, Optional

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.callbacks import CallbackManagerForLLMRun

from config.settings import get_settings
from src.resilience.network import is_online, is_quota_or_auth_error, is_retryable_provider_error
from src.resilience.offline_llm import offline_compose

_last_provider: str = "unknown"
_provider_status_cache: dict[str, str] = {}

OPENAI_MODEL_FALLBACKS = ("gpt-4o-mini", "gpt-4.1-mini", "gpt-4o")
GEMINI_MODEL_FALLBACKS = ("gemini-2.5-flash-lite", "gemini-2.5-flash", "gemini-2.0-flash")


class LLMResult:
    def __init__(self, content: str, provider: str, offline: bool = False):
        self.content = content
        self.provider = provider
        self.offline = offline


def get_last_provider() -> str:
    return _last_provider


def get_provider_status_cache() -> dict[str, str]:
    return dict(_provider_status_cache)


def _set_provider(name: str) -> None:
    global _last_provider
    _last_provider = name


def _timeout_sec() -> int:
    return max(10, get_settings().llm_request_timeout_sec)


def _extract_content(resp: Any) -> str:
    text = resp.content if hasattr(resp, "content") else str(resp)
    if isinstance(text, list):
        parts: list[str] = []
        for block in text:
            if isinstance(block, dict):
                if block.get("text"):
                    parts.append(str(block["text"]))
                elif block.get("type") == "text" and "text" in block:
                    parts.append(str(block["text"]))
            elif isinstance(block, str):
                parts.append(block)
        text = "\n".join(parts)
    return str(text or "").strip()


def _messages_to_text(messages: list[BaseMessage]) -> tuple[str, str]:
    system_parts, user_parts = [], []
    for m in messages:
        if isinstance(m, SystemMessage):
            system_parts.append(str(m.content))
        elif isinstance(m, HumanMessage):
            c = m.content
            if isinstance(c, list):
                user_parts.append(" ".join(
                    b.get("text", "") for b in c if isinstance(b, dict) and b.get("type") == "text"
                ))
            else:
                user_parts.append(str(c))
        elif isinstance(m, AIMessage):
            user_parts.append(f"Assistant: {m.content}")
    return "\n".join(system_parts), "\n".join(user_parts)


def _invoke_with_timeout(llm: BaseChatModel, messages: list[BaseMessage]) -> Any:
    timeout = _timeout_sec()

    def _call():
        return llm.invoke(messages)

    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(_call)
        return future.result(timeout=timeout)


def _build_openai(model: str | None = None):
    settings = get_settings()
    if not settings.openai_api_key:
        return None
    from langchain_openai import ChatOpenAI
    return ChatOpenAI(
        model=model or settings.openai_model,
        api_key=settings.openai_api_key,
        temperature=0.2,
        max_retries=0,
        timeout=_timeout_sec(),
    )


def _build_gemini(model: str | None = None):
    settings = get_settings()
    if not settings.gemini_api_key:
        return None
    from langchain_google_genai import ChatGoogleGenerativeAI
    return ChatGoogleGenerativeAI(
        model=model or settings.gemini_model,
        google_api_key=settings.gemini_api_key,
        temperature=0.2,
        timeout=_timeout_sec(),
        max_retries=0,
    )


def _unique_models(primary: str, fallbacks: tuple[str, ...]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for m in [primary, *fallbacks]:
        if m and m not in seen:
            seen.add(m)
            out.append(m)
    return out


def _provider_chain() -> list[tuple[str, Any]]:
    if not is_online():
        return []
    settings = get_settings()
    pref = (settings.llm_provider or "auto").lower()
    if pref == "offline":
        return []
    chain: list[tuple[str, Any]] = []

    def add_openai():
        for model in _unique_models(settings.openai_model, OPENAI_MODEL_FALLBACKS):
            if not settings.openai_api_key:
                break
            llm = _build_openai(model)
            if llm:
                chain.append((f"openai:{model}", llm))

    def add_gemini():
        for model in _unique_models(settings.gemini_model, GEMINI_MODEL_FALLBACKS):
            if not settings.gemini_api_key:
                break
            llm = _build_gemini(model)
            if llm:
                chain.append((f"gemini:{model}", llm))

    if pref == "gemini":
        add_gemini()
        add_openai()
    elif pref == "openai":
        add_openai()
        add_gemini()
    else:
        add_openai()
        add_gemini()

    return chain


def invoke_messages(messages: list[BaseMessage]) -> LLMResult:
    for name, llm in _provider_chain():
        try:
            resp = _invoke_with_timeout(llm, messages)
            text = _extract_content(resp)
            if text:
                _set_provider(name.split(":")[0] if ":" in name else name)
                _provider_status_cache[name.split(":")[0]] = "ok"
                return LLMResult(content=text, provider=name, offline=False)
        except FuturesTimeoutError:
            _provider_status_cache[name.split(":")[0]] = "timeout"
            continue
        except Exception as e:
            key = name.split(":")[0]
            _provider_status_cache[key] = (
                "quota_or_auth" if is_quota_or_auth_error(e) else "error"
            )
            if is_quota_or_auth_error(e) or is_retryable_provider_error(e):
                continue
            continue

    system, user = _messages_to_text(messages)
    offline_text = offline_compose(system, user)
    _set_provider("offline_rag")
    return LLMResult(content=offline_text, provider="offline_rag", offline=True)


def invoke_text(system: str, user: str, json_mode: bool = False) -> LLMResult:
    messages = [SystemMessage(content=system), HumanMessage(content=user)]
    result = invoke_messages(messages)
    if json_mode and result.offline:
        return LLMResult(
            content=json.dumps({
                "intent": "crop_advisory",
                "confidence": 0.45,
                "recommendation": result.content,
                "safety_notes": "Offline KB mode — verify with field officer.",
            }),
            provider="offline_rag",
            offline=True,
        )
    return result


class ResilientChatModel(BaseChatModel):
    @property
    def _llm_type(self) -> str:
        return "greenharvest-resilient"

    def _generate(
        self,
        messages: list[BaseMessage],
        stop: Optional[list[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        result = invoke_messages(messages)
        message = AIMessage(
            content=result.content,
            response_metadata={"provider": result.provider, "offline": result.offline},
        )
        return ChatResult(generations=[ChatGeneration(message=message)])

    def invoke(self, input: Any, config=None, **kwargs) -> AIMessage:
        messages = input if isinstance(input, list) else [HumanMessage(content=str(input))]
        return self._generate(messages).generations[0].message


def get_resilient_chat_model() -> ResilientChatModel:
    return ResilientChatModel()


def get_primary_chat_model() -> BaseChatModel | None:
    for _name, llm in _provider_chain():
        return llm
    return None


def probe_providers() -> dict[str, str]:
    """Quick health check — used in Admin and tests/."""
    global _provider_status_cache
    status: dict[str, str] = {}
    test = [SystemMessage(content="Reply with exactly: OK"), HumanMessage(content="ping")]

    if not is_online():
        return {"network": "offline", "offline_rag": "ready"}

    settings = get_settings()
    if not settings.openai_api_key:
        status["openai"] = "no_key"
    else:
        ok = False
        for model in _unique_models(settings.openai_model, OPENAI_MODEL_FALLBACKS)[:2]:
            llm = _build_openai(model)
            if not llm:
                continue
            try:
                r = _invoke_with_timeout(llm, test)
                if _extract_content(r):
                    status["openai"] = f"ok ({model})"
                    ok = True
                    break
            except FuturesTimeoutError:
                status["openai"] = "timeout"
            except Exception as e:
                status["openai"] = "quota_or_auth" if is_quota_or_auth_error(e) else "error"
        if not ok and "openai" not in status:
            status["openai"] = status.get("openai", "error")

    if not settings.gemini_api_key:
        status["gemini"] = "no_key"
    else:
        ok = False
        for model in _unique_models(settings.gemini_model, GEMINI_MODEL_FALLBACKS)[:2]:
            llm = _build_gemini(model)
            if not llm:
                continue
            try:
                r = _invoke_with_timeout(llm, test)
                if _extract_content(r):
                    status["gemini"] = f"ok ({model})"
                    ok = True
                    break
            except FuturesTimeoutError:
                status["gemini"] = "timeout"
            except Exception as e:
                status["gemini"] = "quota_or_auth" if is_quota_or_auth_error(e) else "error"
        if not ok and status.get("gemini") not in ("ok",) and not str(status.get("gemini", "")).startswith("ok"):
            status.setdefault("gemini", "error")

    status["offline_rag"] = "ready"
    _provider_status_cache = {k: v for k, v in status.items() if k != "network"}
    return status
