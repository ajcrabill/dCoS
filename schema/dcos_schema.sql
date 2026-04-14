-- Digital Chief of Staff v2 Schema
-- Enhanced schema with relationship intelligence, obligation dependencies,
-- learning rules, and autonomy tracking

PRAGMA foreign_keys = ON;

-- ============================================================================
-- Core Tables (from v1)
-- ============================================================================

CREATE TABLE IF NOT EXISTS people (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  organization TEXT,
  role TEXT,
  stakeholder_class TEXT NOT NULL DEFAULT 'unknown_external',
  autonomy_override TEXT DEFAULT 'inherit',
  relationship_intensity INTEGER CHECK (relationship_intensity BETWEEN 1 AND 5),
  tone_profile TEXT,
  response_sla TEXT,
  never_autonomous_send INTEGER NOT NULL DEFAULT 0,
  sensitive_memory_flag INTEGER NOT NULL DEFAULT 0,
  notes_path TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS person_emails (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  person_id INTEGER NOT NULL,
  email TEXT NOT NULL UNIQUE,
  is_primary INTEGER NOT NULL DEFAULT 0,
  FOREIGN KEY(person_id) REFERENCES people(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS threads (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  external_system TEXT NOT NULL,
  external_id TEXT NOT NULL,
  subject TEXT,
  stakeholder_risk TEXT,
  status TEXT NOT NULL DEFAULT 'open',
  last_activity_at TEXT,
  response_due_at TEXT,
  novelty_score REAL,
  summary TEXT,
  UNIQUE(external_system, external_id)
);

CREATE TABLE IF NOT EXISTS obligations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  source_type TEXT NOT NULL,
  source_id TEXT,
  status TEXT NOT NULL DEFAULT 'open',
  priority TEXT NOT NULL DEFAULT 'moderate',
  importance_score REAL,
  urgency_score REAL,
  owner TEXT NOT NULL DEFAULT 'self',
  due_at TEXT,
  waiting_on_person_id INTEGER,
  waiting_on_since TEXT,
  recommended_next_action TEXT,
  risk_tier TEXT,
  reversible_action_possible INTEGER NOT NULL DEFAULT 1,
  notes_path TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  event_type TEXT NOT NULL,
  source_system TEXT NOT NULL,
  source_id TEXT,
  payload_json TEXT,
  observed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS workflow_runs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  trigger_type TEXT NOT NULL,
  workflow_name TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'queued',
  lease_owner TEXT,
  started_at TEXT,
  completed_at TEXT,
  policy_decision TEXT,
  cost_metrics_json TEXT,
  latency_ms INTEGER,
  error_code TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS draft_actions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  workflow_run_id INTEGER NOT NULL,
  action_type TEXT NOT NULL,
  target_entity_type TEXT,
  target_entity_id TEXT,
  content TEXT,
  confidence REAL,
  novelty_score REAL,
  requires_approval INTEGER NOT NULL DEFAULT 1,
  approval_reason TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(workflow_run_id) REFERENCES workflow_runs(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS approvals (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  draft_action_id INTEGER NOT NULL,
  decision TEXT NOT NULL,
  reviewer TEXT NOT NULL DEFAULT 'self',
  reason TEXT,
  decided_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(draft_action_id) REFERENCES draft_actions(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS policy_rules (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  rule_name TEXT NOT NULL UNIQUE,
  scope TEXT NOT NULL,
  match_json TEXT NOT NULL,
  decision TEXT NOT NULL,
  confidence_threshold REAL,
  novelty_threshold REAL,
  reversible_only INTEGER NOT NULL DEFAULT 0,
  priority_limit TEXT,
  enabled INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS evaluation_records (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  workflow_run_id INTEGER NOT NULL,
  workflow_name TEXT NOT NULL,
  benchmark_slice TEXT,
  outcome TEXT NOT NULL,
  false_positive INTEGER NOT NULL DEFAULT 0,
  false_negative INTEGER NOT NULL DEFAULT 0,
  human_edit_distance REAL,
  confidence REAL,
  calibration_bucket TEXT,
  notes TEXT,
  reviewed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(workflow_run_id) REFERENCES workflow_runs(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS memory_candidates (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  candidate_type TEXT NOT NULL,
  source_workflow_run_id INTEGER,
  source_entity_type TEXT,
  source_entity_id TEXT,
  content TEXT NOT NULL,
  recurrence_count INTEGER NOT NULL DEFAULT 1,
  promotion_status TEXT NOT NULL DEFAULT 'pending',
  sensitive_flag INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(source_workflow_run_id) REFERENCES workflow_runs(id)
);

CREATE TABLE IF NOT EXISTS daily_digest_items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  digest_date TEXT NOT NULL,
  item_type TEXT NOT NULL,
  title TEXT NOT NULL,
  body TEXT,
  source_ref TEXT,
  priority_rank INTEGER,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- NEW: Relationship Intelligence
-- ============================================================================

CREATE TABLE IF NOT EXISTS relationships (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  person_id INTEGER NOT NULL UNIQUE,
  relationship_type TEXT,  -- direct_report, peer, manager, client, coach, vendor, etc
  interaction_style TEXT,  -- formal, casual, detailed, brief, etc
  preferred_contact_mode TEXT,  -- email, call, meeting, async
  contact_frequency_days INTEGER,  -- how often should they hear from you?
  last_contact TEXT,  -- YYYY-MM-DD
  topics_of_interest TEXT,  -- JSON array
  communication_preferences TEXT,  -- JSON object
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(person_id) REFERENCES people(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS relationship_history (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  person_id INTEGER NOT NULL,
  interaction_type TEXT,  -- email, call, meeting, message, etc
  sentiment TEXT,  -- positive, neutral, negative
  summary TEXT,
  context TEXT,
  date_at TEXT,  -- YYYY-MM-DD
  FOREIGN KEY(person_id) REFERENCES people(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS relationship_insights (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  person_id INTEGER NOT NULL,
  insight_type TEXT,  -- gap, opportunity, milestone, change
  description TEXT,
  suggested_action TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(person_id) REFERENCES people(id) ON DELETE CASCADE
);

-- ============================================================================
-- NEW: Obligation Dependencies & Intelligence
-- ============================================================================

CREATE TABLE IF NOT EXISTS obligation_dependencies (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  obligation_id INTEGER NOT NULL,
  depends_on_obligation_id INTEGER NOT NULL,
  constraint_type TEXT,  -- must_complete_first, must_complete_before, blocks_other, provides_input_to
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(obligation_id, depends_on_obligation_id),
  FOREIGN KEY(obligation_id) REFERENCES obligations(id) ON DELETE CASCADE,
  FOREIGN KEY(depends_on_obligation_id) REFERENCES obligations(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS obligation_analytics (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  obligation_id INTEGER NOT NULL,
  days_until_due INTEGER,
  blocking_other_count INTEGER,
  blocked_by_count INTEGER,
  critical_path_depth INTEGER,  -- how deep in dependency chain
  estimated_effort_hours REAL,
  estimated_completion_date TEXT,
  risk_flag_reason TEXT,
  time_crunch_warning INTEGER,  -- 1 if too many due same day
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(obligation_id),
  FOREIGN KEY(obligation_id) REFERENCES obligations(id) ON DELETE CASCADE
);

-- ============================================================================
-- NEW: Learning Rules & Autonomy
-- ============================================================================

CREATE TABLE IF NOT EXISTS learning_rules (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  rule_id TEXT NOT NULL UNIQUE,
  rule_type TEXT NOT NULL,  -- email_triage, obligation_priority, scheduling, etc
  pattern TEXT NOT NULL,
  action TEXT NOT NULL,
  confidence REAL DEFAULT 0.0,  -- 0-1, from user feedback
  created_by TEXT,  -- who created this rule
  notes TEXT,
  applications_count INTEGER DEFAULT 0,
  correct_count INTEGER DEFAULT 0,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  disabled_at TEXT,  -- NULL if active, set when rule retired
  disabled_reason TEXT
);

CREATE TABLE IF NOT EXISTS rule_feedback (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  rule_id INTEGER NOT NULL,
  outcome TEXT,  -- what the rule decided
  correct INTEGER,  -- 1 if correct, 0 if wrong
  feedback TEXT,  -- user feedback
  recorded_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(rule_id) REFERENCES learning_rules(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS autonomy_transitions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  workflow_name TEXT NOT NULL,
  transition_type TEXT NOT NULL,  -- unlocked, revoked, reset
  reason TEXT,
  metrics_snapshot TEXT,  -- JSON with metrics at time of transition
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- NEW: Calendar Intelligence
-- ============================================================================

CREATE TABLE IF NOT EXISTS calendar_patterns (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  pattern_type TEXT NOT NULL,  -- busy_window, preferred_meeting_time, context_switch_cost, etc
  description TEXT,
  day_of_week INTEGER,
  hour_of_day INTEGER,
  frequency_count INTEGER,
  impact_assessment TEXT,  -- high, medium, low
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS protected_time_blocks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  day_of_week INTEGER,  -- 0-6, or NULL for all days
  start_hour INTEGER,
  end_hour INTEGER,
  block_type TEXT,  -- deep_work, admin, personal, break
  recurring INTEGER DEFAULT 1,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- NEW: Predictive Planning
-- ============================================================================

CREATE TABLE IF NOT EXISTS predictive_recommendations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  recommendation_type TEXT NOT NULL,  -- deadline_approaching, dependency_blocking, relationship_gap, time_optimization, etc
  target_entity_type TEXT,  -- obligation, person, project
  target_entity_id TEXT,
  priority_score REAL,
  description TEXT,
  suggested_action TEXT,
  action_deadline TEXT,
  status TEXT DEFAULT 'pending',  -- pending, acknowledged, completed, dismissed
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- Indexes for Performance
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_obligations_status ON obligations(status);
CREATE INDEX IF NOT EXISTS idx_obligations_due_at ON obligations(due_at);
CREATE INDEX IF NOT EXISTS idx_obligations_person ON obligations(waiting_on_person_id);

CREATE INDEX IF NOT EXISTS idx_people_email ON person_emails(email);
CREATE INDEX IF NOT EXISTS idx_people_class ON people(stakeholder_class);

CREATE INDEX IF NOT EXISTS idx_relationships_type ON relationships(relationship_type);
CREATE INDEX IF NOT EXISTS idx_relationships_person ON relationships(person_id);

CREATE INDEX IF NOT EXISTS idx_learning_rules_type ON learning_rules(rule_type);
CREATE INDEX IF NOT EXISTS idx_learning_rules_disabled ON learning_rules(disabled_at);

CREATE INDEX IF NOT EXISTS idx_predictive_rec_type ON predictive_recommendations(recommendation_type);
CREATE INDEX IF NOT EXISTS idx_predictive_rec_status ON predictive_recommendations(status);

CREATE INDEX IF NOT EXISTS idx_workflow_runs_name ON workflow_runs(workflow_name);
CREATE INDEX IF NOT EXISTS idx_workflow_runs_status ON workflow_runs(status);
