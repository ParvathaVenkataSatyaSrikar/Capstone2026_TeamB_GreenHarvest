"""SQLite schema definitions."""
SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS farmers (
    farmer_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    district TEXT NOT NULL,
    crop TEXT NOT NULL,
    land_acres REAL,
    irrigation_type TEXT,
    language TEXT DEFAULT 'english',
    crop_stage TEXT,
    phone TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS interactions (
    interaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    farmer_id TEXT NOT NULL,
    query_text TEXT NOT NULL,
    response_text TEXT,
    intent TEXT,
    language TEXT,
    confidence REAL,
    escalated INTEGER DEFAULT 0,
    agent_trace TEXT,
    citations TEXT,
    response_time_ms INTEGER,
    review_status TEXT DEFAULT 'auto_approved',
    draft_response TEXT,
    human_edited_response TEXT,
    reviewed_by TEXT,
    reviewed_at TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (farmer_id) REFERENCES farmers(farmer_id)
);

CREATE TABLE IF NOT EXISTS cases (
    case_id INTEGER PRIMARY KEY AUTOINCREMENT,
    interaction_id INTEGER,
    farmer_id TEXT NOT NULL,
    priority TEXT DEFAULT 'medium',
    status TEXT DEFAULT 'open',
    assigned_role TEXT DEFAULT 'field_officer',
    summary TEXT,
    follow_up_notes TEXT,
    review_status TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (interaction_id) REFERENCES interactions(interaction_id),
    FOREIGN KEY (farmer_id) REFERENCES farmers(farmer_id)
);

CREATE TABLE IF NOT EXISTS audit_logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    interaction_id INTEGER,
    user_role TEXT,
    action TEXT,
    model_used TEXT,
    chunk_ids TEXT,
    confidence REAL,
    guardrail_triggered INTEGER DEFAULT 0,
    details TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS outbreak_alerts (
    alert_id INTEGER PRIMARY KEY AUTOINCREMENT,
    district TEXT NOT NULL,
    crop TEXT,
    alert_type TEXT,
    query_count INTEGER,
    message TEXT,
    status TEXT DEFAULT 'active',
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS dealer_requests (
    request_id INTEGER PRIMARY KEY AUTOINCREMENT,
    farmer_id TEXT NOT NULL,
    district TEXT,
    crop TEXT,
    input_type TEXT,
    product_note TEXT,
    phone TEXT,
    status TEXT DEFAULT 'demo_logged',
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (farmer_id) REFERENCES farmers(farmer_id)
);
"""
