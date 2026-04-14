# System Architecture

dCoS is a modular, layered system for personal decision support.

## Three-Layer Architecture

```
┌─────────────────────────────────────────────┐
│         Execution Layer                      │
│  (Backend Executor + Suggested Actions)      │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│         Memory Layer                         │
│  (Observations, Learning, Search)            │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│         Capture Layer                        │
│  (Email, Calendar, Vault, Obligations)      │
└─────────────────────────────────────────────┘
```

## Layer 1: Capture Layer

**Purpose:** Continuously observe your digital life

**Components:**
- `gmail_integration` — Monitor incoming email, extract metadata
- `calendar_integration` — Track calendar events and conflicts
- `vault_indexing` — Index Obsidian notes for context
- `obligation_manager` — Capture tasks and deadlines

**Auto-Capture Hooks (5 domains):**
1. **Email** — From/to, subject, attachments, urgency signals
2. **Calendar** — Attendees, duration, time blocks, conflicts
3. **Vault** — File changes, new notes, referenced people
4. **Obligations** — Tasks, deadlines, dependencies
5. **Rules** — When learned rules trigger

**Output:** Raw observations stored in `observations` table

## Layer 2: Memory Layer

**Purpose:** Learn patterns and improve suggestions over time

**Processes:**

### 2a. Memory Consolidation
- Observations → Consolidations (higher-level facts)
- Stored in `memory_consolidations` table
- Example: "3 emails from Sarah this week" → "Sarah needs attention"

### 2b. Semantic Search
- Observations indexed with vector embeddings (768-dim)
- BM25 keyword search on text
- Hybrid search = vector + keyword + knowledge graph
- Query example: "people I haven't contacted recently"

### 2c. Learning Rules
- Pattern extraction from your feedback
- Bayesian confidence scoring
- Auto-update on contradictions
- Example: "If subject contains 'urgent' → flag for CEO"

### 2d. Memory Decay
- Exponential decay curve (Ebbinghaus model)
- Formula: `decay_factor = 2^(-days_old / half_life)`
- Default half-life: 30 days
- Old memories automatically fade

### 2e. Contradiction Detection
- Flags when observations conflict with learned rules
- Bayesian confidence updates
- Example: "Usually emails to client are long, but this is very short"
- Triggers manual review

**Output:** Learned rules, consolidations, decay markers

## Layer 3: Execution Layer

**Purpose:** Make decisions and suggest actions

**Backend Executors:**
- **Ollama** (recommended) — Local, private, free
- **MLX** — Apple Silicon optimized
- **Claude API** — Cloud, highest quality

**Decision Process:**
1. Backend receives context (recent observations, rules, history)
2. Generates suggested action with reasoning
3. Attaches confidence score
4. Flags for approval if uncertain

**Suggested Actions:**
- Email: Draft response, categorize, flag for review
- Calendar: Suggest schedule optimization, flag conflicts
- Task: Recommend priority, predict deadline
- Relationship: Suggest outreach based on contact frequency

**Output:** Drafted suggestions (never auto-executed)

## Data Flow Diagram

```
┌──────────┐    ┌──────────┐    ┌──────────┐
│  Email   │    │Calendar  │    │  Vault   │
└────┬─────┘    └────┬─────┘    └────┬─────┘
     │               │               │
     └───────────────┼───────────────┘
                     ↓
         ┌─────────────────────┐
         │  Auto-capture hooks │
         │  (Privacy filter)   │
         └──────────┬──────────┘
                    ↓
         ┌─────────────────────┐
         │  observations table │
         │  (Raw data)         │
         └──────────┬──────────┘
                    ↓
    ┌──────────────────────────────────┐
    │     Memory Processing            │
    │ - Consolidation                  │
    │ - Embedding (768-dim)            │
    │ - Learning rules                 │
    │ - Decay calculation              │
    │ - Contradiction detection        │
    └──────────┬───────────────────────┘
               ↓
    ┌──────────────────────────────────┐
    │  Memory Tables                   │
    │ - consolidations                 │
    │ - vector_embeddings              │
    │ - learned_rules                  │
    │ - contradictions                 │
    │ - decay markers                  │
    └──────────┬───────────────────────┘
               ↓
    ┌──────────────────────────────────┐
    │  Backend Executor                │
    │  (Ollama/MLX/Claude)             │
    │  Prompt + Context → Decision     │
    └──────────┬───────────────────────┘
               ↓
       ┌──────────────────┐
       │  Suggested       │
       │  Actions (Draft) │
       │  + Confidence    │
       └────────┬─────────┘
                ↓
           ┌─────────┐
           │  You    │  ← Approve/Reject
           │ Review  │
           └────┬────┘
                ↓
    ┌──────────────────────────────────┐
    │  Your Feedback                   │
    │ → Updates learned rules          │
    │ → Improves future suggestions    │
    │ → Increases confidence           │
    └──────────────────────────────────┘
```

## Module Breakdown

### Core Modules (8)
- `backend_executor` — LLM decision making
- `vault_indexing` — Obsidian integration
- `account_manager` — OAuth and credentials
- `gmail_integration` — Email capture and drafting
- `calendar_integration` — Calendar events and scheduling
- `obligation_manager` — Task tracking
- `relationship_intelligence` — People and contact tracking
- `learning_rules` — Pattern learning from feedback
- `predictive_planning` — Schedule optimization

### Memory Modules (5)
- `embedding_provider` — Vector embedding (Ollama/MLX)
- `memory_decay` — Ebbinghaus curve decay and pruning
- `vector_search` — Hybrid semantic search
- `observation_capture` — Central auto-capture system
- `contradiction_detector` — Conflict flagging and confidence updates
- `privacy_filter` — Sensitive data redaction

## Database Schema

**Core Tables:**
- `observations` — Raw captured data
- `memory_consolidations` — Aggregated facts
- `vector_embeddings` — 768-dim embeddings for search
- `learned_rules` — Extracted patterns with confidence
- `contradiction_flags` — Conflicts needing review
- `memory_decay_log` — Decay calculations and pruning

**Supporting Tables:**
- `relationships` — People and contact metadata
- `email_drafts` — Suggested responses
- `calendar_events` — Event snapshots
- `obligations` — Tasks and deadlines
- `feedback_log` — Your corrections and approvals

## Key Design Principles

1. **Privacy-First** — Sensitive data redacted before storage
2. **Transparent** — All suggestions drafted, nothing auto-executed
3. **Learnable** — Improves from feedback (300+ examples to unlock autonomy)
4. **Non-Destructive** — No auto-deletion; memory only ages via decay
5. **Modular** — Independent layers and modules
6. **Local-First** — Works offline with local LLM
7. **Extensible** — Easy to add new sources and actions

## Performance Characteristics

**Latency:**
- Capture: <100ms (local hooks)
- Search: <500ms (hybrid search)
- Suggestion generation: 1-5s (backend dependent)

**Storage:**
- Baseline: 100 MB
- Per 1000 observations: ~5 MB
- Vector embeddings: ~3 MB per 10k observations

**Compute:**
- Ollama (local): Uses your GPU or CPU
- MLX (Apple Silicon): ~50-150ms per suggestion
- Claude (cloud): ~1-3s per suggestion

## Scaling Considerations

**For high-volume users (1000+ observations/week):**
- Memory decay becomes critical (automatic pruning)
- Consolidation necessary (aggregate observations)
- Search indexing important (hybrid search prevents full-table scans)

**For long-running instances:**
- Database should be backed up regularly
- Vector embeddings can be rebuilt if needed
- Learned rules should be reviewed periodically

---

See `FEATURES.md` for what each capability does in practice.
