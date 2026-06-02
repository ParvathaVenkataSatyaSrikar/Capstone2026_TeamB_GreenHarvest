# Deployment Guide

## Prerequisites

| Requirement | Version |
|-------------|---------|
| Python | 3.10 or later |
| pip | Latest stable |
| Network | Required for LLM and embedding APIs (optional for offline mode) |

## Installation

### 1. Clone and enter the project

```powershell
cd Project
```

### 2. Create virtual environment

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure environment

```powershell
copy .env.example .env
```

Edit `.env` and set the following variables:

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | Recommended | Primary LLM and embedding provider |
| `OPENAI_API_KEY` | Optional | First-tier LLM when `LLM_PROVIDER=auto` |
| `TAVILY_API_KEY` | Optional | Live web search for market/scheme context |
| `LLM_PROVIDER` | Optional | `auto` (default), `openai`, `gemini`, or `offline` |

Run `python scripts/fix_env.py` if `.env` parsing fails due to formatting issues.

### 4. Initialize data

```powershell
python scripts/init_db.py
python scripts/seed_demo_accounts.py
python scripts/ingest_kb.py
```

**Knowledge base ingest notes:**

- First FAISS ingest may take 1–3 hours depending on network speed.
- Progress is saved under `data/faiss_index/`; re-run `ingest_kb.py` to resume.
- Without `GEMINI_API_KEY`, the system uses keyword search over all knowledge base chunks.
- Gemini free tier limits embedding calls (~1,000/day); full ingest may require multiple days.

### 5. Validate deployment

```powershell
python scripts/verify_auth.py
python scripts/smoke_test.py
python scripts/check_ready.py
```

### 6. Start application

```powershell
streamlit run app.py
```

Default URL: `http://localhost:8501`

## Configuration reference

| Setting | File | Default |
|---------|------|---------|
| Streamlit performance | `.streamlit/config.toml` | `fileWatcherType = "none"` |
| Database path | `config/settings.py` | `data/greenharvest.db` |
| Knowledge base | `config/settings.py` | `knowledge_base/` |
| Escalation threshold | `.env` | `ESCALATION_CONFIDENCE_THRESHOLD=0.55` |
| Retrieval minimum score | `.env` | `RETRIEVAL_MIN_SCORE=0.35` |

## Operational procedures

### Database backup

Copy `data/greenharvest.db` while Streamlit is stopped to avoid write conflicts.

### Re-seed demo data

Stop Streamlit, then:

```powershell
python scripts/seed_demo_accounts.py
```

### Rebuild knowledge index

```powershell
python scripts/ingest_kb.py
```

### Health monitoring

Run `python scripts/smoke_test.py` before demonstrations or after configuration changes.

## Production considerations

The current build is a functional prototype. Production deployment should address:

| Area | Recommendation |
|------|----------------|
| Authentication | Replace demo passwords; integrate SSO or OAuth |
| Database | Migrate SQLite to PostgreSQL or managed SQL |
| Secrets | Use a secrets manager; never commit `.env` |
| Hosting | Deploy Streamlit behind HTTPS reverse proxy |
| Scaling | Single-writer SQLite limits concurrent users |
| API keys | Rate limiting and quota monitoring for LLM providers |
| Data privacy | Encrypt PII; define retention policies for audit logs |

## Troubleshooting

| Issue | Resolution |
|-------|------------|
| Weak or missing RAG answers | Set `GEMINI_API_KEY` and run `ingest_kb.py` |
| Streamlit slow reload | Confirm `.streamlit/config.toml` has `fileWatcherType = "none"` |
| Database locked | Stop Streamlit before running seed or init scripts |
| API quota exceeded | System falls back to offline knowledge; retry ingest next day |
| No internet | Yellow status banner; local crop guides still available |
| `pip install` stops or times out | Use `pip install --default-timeout=300 -r requirements.txt` or install in stages (see below) |
| `smoke_test.py` appears frozen | Default mode is **offline** (fast). Use `python scripts/smoke_test.py` without `--live` unless you are testing live API keys |
| Streamlit warnings in scripts | `missing ScriptRunContext` is normal when running `scripts/*.py` outside `streamlit run` — safe to ignore |

### Slow or failing pip install

Large packages (`faiss-cpu`, `langchain`, `streamlit`) can take several minutes on slow or restricted networks. Try:

```powershell
python -m pip install --upgrade pip
pip install --default-timeout=300 wheel
pip install --default-timeout=300 streamlit python-dotenv pydantic pydantic-settings truststore pandas plotly
pip install --default-timeout=300 langchain langchain-core langgraph langchain-google-genai langchain-openai langchain-community langchain-text-splitters langchain-tavily
pip install --default-timeout=300 faiss-cpu google-generativeai openai tavily-python Pillow SpeechRecognition pytest
```

Install from a local folder outside cloud-synced directories if downloads are interrupted frequently.

### Smoke test modes

| Command | When to use |
|---------|-------------|
| `python scripts/smoke_test.py` | **Default** — offline pipeline, finishes in ~1–2 min |
| `python scripts/smoke_test.py --live` | Verify real OpenAI/Gemini keys (may take 2–5 min depending on network and API latency) |
