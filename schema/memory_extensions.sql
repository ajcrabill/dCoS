-- dCoS v2 + AgentMemory Schema Additions
-- Run this after schema_v2.sql to add memory & observation tables

-- Observations: Raw captured data from all sources
CREATE TABLE IF NOT EXISTS observations (
    id TEXT PRIMARY KEY,
    observation_type TEXT NOT NULL,  -- email, calendar, obligation, rule, vault
    source TEXT,                      -- gmail, gcal, dcos, obsidian
    raw_data TEXT,                    -- JSON serialized data
    tier TEXT DEFAULT 'working',      -- working, episodic, semantic, procedural
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    importance_score REAL DEFAULT 1.0, -- Starts 1.0, decays over time
    embedded BOOLEAN DEFAULT 0         -- Has embedding been generated?
);

-- FTS5 Index for observation search
CREATE VIRTUAL TABLE IF NOT EXISTS observations_fts
USING fts5(observation_type, source, raw_data, content=observations, content_rowid=id);

-- Memory Consolidations: Higher-level summaries of observations
CREATE TABLE IF NOT EXISTS memory_consolidations (
    id TEXT PRIMARY KEY,
    source_observations TEXT,          -- JSON list of observation IDs
    tier TEXT NOT NULL,                -- episodic, semantic, procedural
    summary TEXT,                      -- Consolidated summary
    created_from_tier TEXT,            -- Which tier this was consolidated from
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    importance_score REAL DEFAULT 0.9
);

-- Contradiction Flags: Flagged contradictions for user review
CREATE TABLE IF NOT EXISTS contradiction_flags (
    id TEXT PRIMARY KEY,
    memory_id TEXT,                    -- ID of rule/relationship being contradicted
    memory_type TEXT,                  -- rule, relationship, obligation
    observation TEXT,                  -- JSON of contradicting observation
    original_confidence REAL,          -- Confidence before contradiction
    updated_confidence REAL,           -- Confidence after Bayesian update
    severity TEXT,                     -- low, medium, high, critical
    flagged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_reviewed BOOLEAN DEFAULT 0,
    user_decision TEXT                 -- accepted, rejected, revised_rule
);

-- Memory Decay Log: Track decay of each memory
CREATE TABLE IF NOT EXISTS memory_decay_log (
    id TEXT PRIMARY KEY,
    memory_id TEXT,                    -- ID of memory being tracked
    memory_type TEXT,                  -- observation, rule, relationship, obligation
    initial_importance REAL,           -- Starting importance score
    current_importance REAL,           -- Current importance after decay
    days_since_creation INT,           -- How old is this memory
    decay_calculated_at TIMESTAMP,     -- When was decay last calculated
    touch_count INT DEFAULT 0,         -- Times memory was accessed (resets decay)
    last_touched_at TIMESTAMP,         -- When was memory last used
    scheduled_for_deletion BOOLEAN DEFAULT 0,
    deletion_scheduled_at TIMESTAMP
);

-- Vector Embeddings: Store embeddings for semantic search
CREATE TABLE IF NOT EXISTS vector_embeddings (
    id TEXT PRIMARY KEY,
    source_type TEXT,                  -- observations, relationships, obligations
    source_id TEXT,                    -- ID of source entity
    embedding_data TEXT,               -- JSON array of floats
    model_used TEXT,                   -- ollama, mlx, etc.
    embedding_dim INT,                 -- Dimension (768 for nomic-embed-text)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_observations_created_at ON observations(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_observations_importance ON observations(importance_score DESC);
CREATE INDEX IF NOT EXISTS idx_observations_type ON observations(observation_type);
CREATE INDEX IF NOT EXISTS idx_contradiction_flags_reviewed ON contradiction_flags(user_reviewed);
CREATE INDEX IF NOT EXISTS idx_memory_decay_deletion ON memory_decay_log(scheduled_for_deletion);
CREATE INDEX IF NOT EXISTS idx_vector_embeddings_source ON vector_embeddings(source_type, source_id);
