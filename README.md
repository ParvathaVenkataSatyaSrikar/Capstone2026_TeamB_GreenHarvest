# GreenHarvest Farmer Support System

Agentic AI platform for agricultural support — grounded crop advisory, human-in-the-loop expert review, role-based portals, and operational analytics.

Built as a demonstration prototype using **LangGraph**, **RAG (FAISS)**, **Streamlit**, and **SQLite**.

---

## Features

| Feature | Description |
|---------|-------------|
| **AI Crop Advisor** | LangGraph pipeline: intake → intent → RAG → context → recommendation → HITL |
| **Grounded answers** | Retrieval over 3,400+ crop, pest, scheme, and region guides |
| **Context-aware** | Weather, soil, market, and crop-stage data from structured mocks |
| **Human-in-the-loop** | Field officers approve or edit low-confidence / sensitive answers |
| **Role-based portals** | Separate experiences for farmers, field officers, and administrators |
| **Multilingual** | English, Hindi, Telugu, Tamil, Marathi, Punjabi |
| **Resilience** | OpenAI → Gemini → offline knowledge fallback |
| **Governance** | Audit logs, confidence scoring, guardrails |
| **Early warning** | District-level pest-query clustering for outbreak alerts |

---

## Architecture (high level)

```
Farmer UI (Streamlit)
       ↓
support_service.py
       ↓
LangGraph pipeline (8 nodes)
       ↓
RAG (FAISS / keyword) + CSV integrations + LLM
       ↓
SQLite (interactions, cases, audit)
       ↓
Officer HITL review (when needed)
```

Detailed design: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

---

## Prerequisites

- **Python 3.10+**
- **pip**
- Optional: **GEMINI_API_KEY** and/or **OPENAI_API_KEY** for live LLM and FAISS embeddings
- Optional: **TAVILY_API_KEY** for live web context on market/scheme queries

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/ParvathaVenkataSatyaSrikar/Capstone2026_TeamB_GreenHarvest.git
cd Capstone2026_TeamB_GreenHarvest
```

### 2. Create a virtual environment

**Windows (PowerShell)**

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

If installation is slow or times out, increase the pip timeout or install dependencies in stages — see [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md#slow-or-failing-pip-install).

### 3. Configure environment variables

```powershell
copy .env.example .env    # Windows
# cp .env.example .env    # macOS / Linux
```

Edit `.env` and add your API keys. **Never commit `.env` to Git** — it is listed in `.gitignore`.

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | Recommended | Primary LLM and embeddings |
| `OPENAI_API_KEY` | Optional | First-tier LLM when `LLM_PROVIDER=auto` |
| `TAVILY_API_KEY` | Optional | Live web snippets for market/scheme context |
| `LLM_PROVIDER` | Optional | `auto` (default), `openai`, `gemini`, or `offline` |
| `LLM_REQUEST_TIMEOUT_SEC` | Optional | API timeout in seconds (default: 35) |

### 4. Initialize data

```bash
python scripts/init_db.py
python scripts/seed_demo_accounts.py
python scripts/ingest_kb.py
```

Knowledge-base ingest may take time on first run; progress is saved under `data/faiss_index/`. Without an API key, the app uses keyword search over all guides.

### 5. Verify and run

```bash
python scripts/smoke_test.py
streamlit run app.py
```

Open **http://localhost:8501**

---

## Demo credentials

| Role | Username | Password |
|------|----------|----------|
| Farmer | `farmer_f001` | `farmer123` |
| Field Officer | `officer1` | `officer2026` |
| Administrator | `admin` | `admin2026` |

New farmers can register via **Sign Up**.

---

## Application modules

| Role | Modules |
|------|---------|
| **Farmer** | AI Crop Advisor, My Queries, farm profile, schemes, dealers |
| **Field Officer** | Human Review, Field Cases |
| **Administrator** | Analytics, Governance, Knowledge, Settings |

| AI component | Purpose |
|--------------|---------|
| **AI Crop Advisor** | Full LangGraph + RAG crop pipeline |
| **Portal Assistant** | Sidebar application help (not crop advice) |

---

## Verification scripts

```bash
python scripts/verify_auth.py
python scripts/smoke_test.py          # offline mode by default (fast)
python scripts/smoke_test.py --live   # test real API keys
python scripts/check_ready.py
python scripts/eval_intent_classification.py
python -m pytest tests/
```

---

## Project structure

```
├── app.py                 # Application entry point
├── config/                # Settings and environment loading
├── pages/                 # Streamlit UI (role-based portals)
├── src/
│   ├── graph/             # LangGraph workflow and nodes
│   ├── services/          # support_service, hitl_service
│   ├── chains/            # LLM chains and Pydantic schemas
│   ├── rag/               # FAISS retrieval and embeddings
│   ├── integrations/      # Weather, soil, market CSV mocks
│   ├── auth/              # Authentication and RBAC
│   ├── db/                # SQLite models and repository
│   ├── governance/        # Audit, guardrails, confidence
│   ├── helper/            # Portal Assistant
│   └── ui/                # Shared UI components
├── assets/images/         # UI photography (bundled with the repo)
├── knowledge_base/        # Agricultural guides for RAG
├── data/                  # CSV assets (DB/index generated locally)
├── scripts/               # Setup, ingest, validation
├── tests/                 # Unit tests
└── docs/                  # Technical documentation
```

---

## Documentation

| Document | Description |
|----------|-------------|
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | System design and LangGraph workflow |
| [docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md) | Module map |
| [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) | Installation, operations, troubleshooting |
| [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) | Developer guide |
| [docs/REQUIREMENTS.md](docs/REQUIREMENTS.md) | Requirements traceability |
| [docs/USER_STORIES.md](docs/USER_STORIES.md) | Persona-based requirements |
| [docs/AUTH_AND_RBAC.md](docs/AUTH_AND_RBAC.md) | Security model |
| [docs/RESILIENCE.md](docs/RESILIENCE.md) | LLM and RAG fallback behaviour |
| [docs/DEMONSTRATION.md](docs/DEMONSTRATION.md) | Demo scenarios |

---

## Security notes

- **`.env` is gitignored** — contains API keys; use `.env.example` as a template only.
- **`data/greenharvest.db`** is gitignored — each clone generates its own database via `init_db.py`.
- Demo passwords are for prototype use only; replace before any production deployment.
- Staff roles also accept `STAFF_DEMO_PASSWORD` from `.env` (see `.env.example`) as an optional alternate to the table above.

---

## Scope and limitations

This is a **demonstration prototype**. Government APIs, payment gateways, and mandi feeds use **mock CSV data**. Production use requires additional hardening — see [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

---

## Tech stack

Python · Streamlit · LangGraph · LangChain · FAISS · Gemini / OpenAI · Pydantic · SQLite
