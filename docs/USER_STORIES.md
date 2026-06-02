# User Stories

Functional requirements organized by persona.

## Farmer

### Registration and onboarding

**As a new farmer**, I want to register with guided onboarding so I understand the application before submitting my first query.

**Acceptance criteria:**
- Sign-up collects name, username, password, district, and crop
- Onboarding assistant supports registration (works offline)
- System creates farmer profile and authenticates the new user

### Crop advisory

**As a farmer**, I want AI-powered crop guidance that remains available when API quotas are exhausted or the network is unavailable.

**Acceptance criteria:**
- System falls back from cloud LLM to offline knowledge automatically
- Status bar indicates active LLM tier and network state
- Login: `farmer_f001` / `farmer123` (linked to farmer F001)
- Navigation: Home → AI Crop Advisor → My Queries
- Farmer role cannot access officer or admin pages
- Crop AI uses LangGraph + RAG; sensitive answers require officer approval
- Portal Assistant in sidebar explains application usage (not crop treatment)

## Field Officer

### Human review

**As a field officer**, I want a dedicated portal to review AI-generated drafts before farmers receive them.

**Acceptance criteria:**
- Login: `officer1` / `officer2026`
- Human Review: approve, edit, or reject pending queries
- Field Cases: view escalations and district alerts
- Officer role cannot access farmer chat as a farmer account

## Administrator

### Operations and governance

**As an administrator**, I want analytics, governance, and knowledge management in a single portal.

**Acceptance criteria:**
- Login: `admin` / `admin2026`
- Access to Analytics, Governance, Knowledge, and Settings
- Supervisor access to Human Review and Field Cases
- Role change requires logout (no in-session role switching)

## Portal Assistant (all roles)

**As any authenticated user**, I want an application guide that understands my role and the current system state.

**Acceptance criteria:**
- Sidebar Portal Assistant answers navigation, HITL, and module questions
- Portal Assistant does not replace AI Crop Advisor for pest and crop advice
- Responses respect the selected answer language
