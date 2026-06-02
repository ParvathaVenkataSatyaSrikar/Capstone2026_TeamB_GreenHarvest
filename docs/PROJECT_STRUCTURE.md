# Project Structure

This document describes the repository layout for GreenHarvest Farmer Support System.

## High-level architecture

```
┌─────────────────────────────────────────────────────────────┐
│  pages/          Streamlit UI (Farmer / Officer / Admin)    │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│  src/services/     support_service.py → LangGraph pipeline  │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│  src/graph/        LangGraph pipeline (intake → answer)      │
│  src/chains/       LLM + Pydantic structured output         │
│  src/rag/          FAISS / keyword search on knowledge_base │
│  src/integrations/ CSV-backed weather, soil, market, etc.   │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│  data/             SQLite + CSV mocks + faiss_index/        │
│  knowledge_base/   Approved crop / pest / region guides     │
└─────────────────────────────────────────────────────────────┘
```

## Top-level directories

| Path | Purpose |
|------|---------|
| `app.py` | Application entry; redirects to login or role home |
| `config/` | Environment configuration (`settings.py`) |
| `pages/` | Streamlit screens (numbered for menu order) |
| `src/` | Application logic (Python packages) |
| `data/` | SQLite database, CSV demo data, FAISS index |
| `knowledge_base/` | 3,400+ markdown guides for RAG |
| `scripts/` | Database init, KB ingest, validation |
| `tests/` | Unit tests |
| `docs/` | Technical documentation |

## Streamlit pages

| File | Role | Function |
|------|------|----------|
| `0_Login.py` | All | Authentication |
| `00_Sign_Up.py` | Public | Farmer registration |
| `10_Farmer_Home.py` | Farmer | Dashboard |
| `2_Farmer_AI_Advisor.py` | Farmer | AI crop chat and photo diagnosis |
| `3_Farmer_My_Queries.py` | Farmer | Query history and approved answers |
| `20_Officer_Home.py` | Field Officer | Dashboard |
| `4_Officer_Human_Review.py` | Field Officer | HITL approve/edit workflow |
| `5_Officer_Field_Cases.py` | Field Officer | Escalations and outbreak alerts |
| `30_Admin_Home.py` | Administrator | Dashboard |
| `6_Admin_Analytics.py` | Administrator | KPIs, charts, outbreak detection |
| `7_Admin_Governance.py` | Administrator | Audit log export |
| `8_Admin_Knowledge.py` | Administrator | Knowledge base and ingest status |
| `9_Admin_Settings.py` | Administrator | LLM configuration probe |

## Source packages (`src/`)

| Package | Responsibility |
|---------|----------------|
| `graph/` | LangGraph workflow — `workflow.py`, `nodes.py`, `state.py` |
| `services/` | `support_service.py`, `hitl_service.py` |
| `chains/` | LangChain LCEL, Pydantic schemas, intent chains |
| `rag/` | FAISS ingest/retrieve, embeddings, crop catalog |
| `integrations/` | CSV-backed market, weather, soil, insurance |
| `resilience/` | LLM router, safe pipeline, network checks |
| `auth/` | Users, session, RBAC, demo seed |
| `db/` | SQLite models and repository |
| `governance/` | Audit log, guardrails, confidence scoring |
| `ui/` | Portal sidebar, chat UI, theme, components |
| `helper/` | Portal Assistant (application help) |
| `advisory/` | Schemes, lifecycle, weather alerts |
| `analytics/` | Outbreak cluster detection |
| `vision/` | Crop photo diagnosis |
| `i18n/` | Multilingual farmer text |
| `onboarding/` | Registration assistant |

## Data layer

| Asset | Purpose |
|-------|---------|
| `greenharvest.db` | Users, farmers, interactions, cases, audit logs |
| `weather.csv`, `soil_reports.csv`, `market_prices.csv` | Deterministic integration mocks |
| `crop_calendar.csv`, `scheme_eligibility.csv` | Advisory context |
| `faiss_index/` | Vector store (created by `scripts/ingest_kb.py`) |
| `kb_chunks_cache.json` | KB chunk cache for ingest resume |

## Scripts

| Script | Purpose |
|--------|---------|
| `init_db.py` | Initialize database schema |
| `seed_demo_accounts.py` | Seed demo farmers, officers, and sample data |
| `ingest_kb.py` | Build or resume FAISS index |
| `build_mega_knowledge_base.py` | Regenerate knowledge base markdown files |
| `enrich_data_assets.py` | Refresh CSV mock data |
| `smoke_test.py` | End-to-end health check |
| `eval_intent_classification.py` | Intent classification evaluation |
| `verify_auth.py` | Validate demo credentials |
| `check_ready.py` | Pre-deployment readiness check |
| `fix_env.py` | Repair malformed `.env` files |

## LangGraph pipeline order

`intake` → `classify_intent` → `retrieve_knowledge` → `build_context` → `generate_recommendation` → `staff_summary` → `escalation_check` → `human_review_gate`

## Code review walkthrough (recommended order)

1. `app.py` and `pages/0_Login.py` — authentication and roles
2. `pages/2_Farmer_AI_Advisor.py` → `src/ui/chat_ui.py`
3. `src/services/support_service.py`
4. `src/graph/workflow.py` and `nodes.py`
5. `src/rag/retriever.py`
6. `src/integrations/` — CSV integration layer
7. `pages/4_Officer_Human_Review.py` — HITL workflow
8. `pages/6_Admin_Analytics.py` — analytics and outbreak detection
