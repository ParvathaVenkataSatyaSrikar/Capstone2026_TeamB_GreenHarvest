# Requirements Traceability

Source: *Agentic AI Farmer Support System* — GreenHarvest Farmer Support.

## Core AI agents

| # | Requirement | Status | Implementation |
|---|-------------|--------|----------------|
| 1 | Farmer Query Intake | Complete | `src/graph/nodes.py` → `node_intake` |
| 2 | Intent Classification | Complete | `node_classify_intent` |
| 3 | Knowledge Retrieval (RAG) | Complete | `node_retrieve_knowledge`, `src/rag/` |
| 4 | Context Analysis | Complete | `node_build_context` |
| 5 | Recommendation Agent | Complete | `node_generate_recommendation` |
| 6 | Escalation Agent | Complete | `node_escalation_check` |
| 7 | Interaction Summary | Complete | `node_staff_summary` |

## Key features

| # | Requirement | Status | Implementation |
|---|-------------|--------|----------------|
| 8 | Farmer onboarding | Complete | `pages/00_Sign_Up.py` |
| 9 | Crop advisory | Complete | AI Crop Advisor + knowledge base |
| 10 | Weather-aware recommendations | Complete | `src/integrations/weather.py` |
| 11 | Soil-health guidance | Complete | `src/integrations/soil.py` |
| 12 | Market price / mandi | Complete | `src/integrations/market.py` |
| 13 | Scheme and insurance support | Complete | Intent routing + knowledge base |
| 14 | Expert escalation (HITL) | Complete | `node_human_review_gate`, Human Review page |
| 15 | Staff dashboard | Complete | Admin analytics, officer review |

## Architecture requirements

| # | Requirement | Status | Implementation |
|---|-------------|--------|----------------|
| 16 | Web portal | Complete | Streamlit `app.py` + `pages/` |
| 17 | Multi-agent orchestration | Complete | LangGraph `src/graph/workflow.py` |
| 18 | Knowledge layer | Complete | FAISS + Gemini embeddings |
| 19 | Mock integrations | Complete | `src/integrations/` |
| 20 | Governance | Complete | `src/governance/` |
| 21 | Role-based access | Complete | `src/auth/` |

## Deliverables

| # | Requirement | Status | Location |
|---|-------------|--------|----------|
| 22 | Working prototype | Complete | `streamlit run app.py` |
| 23 | Architecture documentation | Complete | `docs/ARCHITECTURE.md` |
| 24 | Agent roles documented | Complete | `docs/DEVELOPMENT.md` |
| 25 | Farmer conversational UI | Complete | AI Crop Advisor |
| 26 | Staff case view | Complete | Human Review, Field Cases |

## Success criteria

| # | Criterion | Status | Notes |
|---|-----------|--------|-------|
| 27 | Intent classification | Complete | Keyword + LLM hybrid |
| 28 | Grounded recommendations | Complete | RAG with citations |
| 29 | High-risk escalation | Complete | Pest, insurance, low confidence |
| 30 | Local-language responses | Complete | Six languages via `src/i18n/` |
| 31 | Audit and traceability | Complete | `audit_logs`, Governance page |

## Multilingual behaviour

1. Sidebar **Answer language** selector (English, Hindi, Telugu, Tamil, Marathi, Punjabi).
2. Preference saved to farmer profile on change.
3. Preference loaded on login.
4. AI Crop Advisor generates responses in the selected language.
5. Pending expert-review messages are translated.
6. Officer-approved answers are translated to the farmer's language.
7. Portal Assistant respects the selected answer language.

## Out of scope

| Item | Status |
|------|--------|
| WhatsApp channel | Not implemented (web only) |
| Voice input | Partial — SpeechRecognition demo in Crop Advisor |
| Real payment transactions | Mock PM-KISAN status only |
| E-commerce checkout | Dealer directory + callback log only |
| Government registry integration | Self-entered profile data only |
| Guaranteed diagnosis | HITL workflow + disclaimers |

## Sample use cases

Demonstration scenarios are documented in [DEMONSTRATION.md](DEMONSTRATION.md).
