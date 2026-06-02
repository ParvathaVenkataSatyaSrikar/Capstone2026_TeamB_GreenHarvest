# Resilience and Fault Tolerance

## LLM provider fallback

| Tier | Condition |
|------|-----------|
| OpenAI | `OPENAI_API_KEY` set and `LLM_PROVIDER=auto` or `openai` |
| Gemini | OpenAI unavailable or `LLM_PROVIDER=gemini` |
| Offline | No API key, quota error, or network failure |

Implementation: `src/resilience/llm_router.py` → `src/chains/llm_factory.py`

The offline tier serves keyword-matched knowledge base snippets and structured templates. The UI displays the active provider tier in the status bar.

## RAG retrieval modes

| Mode | Condition |
|------|-----------|
| FAISS + Gemini embeddings | `GEMINI_API_KEY` set and `scripts/ingest_kb.py` completed |
| Keyword fallback | No API key, embed timeout, or ingest not run |

Implementation: `src/rag/retriever.py`

Keyword fallback searches all knowledge base chunks without vector embeddings. Partial FAISS indexes from interrupted ingest still improve retrieval for embedded chunks.

## Integration context

Mock CSV integrations in `src/integrations/` provide deterministic weather, soil, and market data.

Optional Tavily web search (`TAVILY_API_KEY`) augments market, scheme, and insurance context in `node_build_context`.

## Safe pipeline

`src/resilience/safe_pipeline.py` wraps the LangGraph invocation to prevent UI crashes:

- Catches LLM and network exceptions
- Returns farmer-safe fallback messages
- Logs errors for governance audit

## Network detection

`src/resilience/network.py` checks connectivity and displays a status banner when offline. Offline mode activates automatically; local crop guides remain available.

## UI error handling

| Condition | System response |
|-----------|-----------------|
| No internet | Status banner; local knowledge base answers |
| API quota exceeded | Fallback to offline tier |
| Empty query | Validation warning |
| Malformed `.env` | Run `python scripts/fix_env.py` |

## Configuration

Relevant environment variables in `.env`:

| Variable | Purpose |
|----------|---------|
| `LLM_PROVIDER` | Provider selection (`auto`, `openai`, `gemini`, `offline`) |
| `LLM_REQUEST_TIMEOUT_SEC` | Request timeout (default: 35) |
| `ESCALATION_CONFIDENCE_THRESHOLD` | HITL trigger threshold (default: 0.55) |
| `RETRIEVAL_MIN_SCORE` | Minimum RAG relevance score (default: 0.35) |

See [DEPLOYMENT.md](DEPLOYMENT.md) for operational procedures.
