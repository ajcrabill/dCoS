# Digital Chief of Staff

Your personal AI assistant that learns your patterns, manages your time, and handles your workflows with your explicit approval.

**GitHub:** https://github.com/ajcrabill/dCoS  
**Creator:** AJ Crabill

## What is dCoS?

dCoS is a non-autonomous decision support system that:

- **Observes** your emails, calendar, and obligations in real-time
- **Learns** your patterns and preferences from your feedback
- **Suggests** actions before you make decisions
- **Integrates** with Gmail, Google Calendar, and Obsidian vault
- **Respects** your privacy (local processing, full data control)

It's designed for knowledge workers who want AI assistance *without* surrendering autonomy.

## Core Capabilities

**Email Management**
- Triage incoming messages (draft, categorize, flag for review)
- Suggest responses based on your communication patterns
- Track follow-ups and obligations
- Learn your email categories and urgency rules

**Calendar Intelligence**
- Flag scheduling conflicts and suboptimal patterns
- Suggest deep work time blocks
- Summarize meeting context
- Track time allocation trends

**Obligation Tracking**
- Capture tasks from email and meetings
- Track dependencies and deadlines
- Suggest task order and priorities
- Monitor aging obligations

**Relationship Management**
- Remember contact patterns with key people
- Suggest outreach when someone falls below contact frequency
- Track relationship context and history
- Alert on important stakeholder updates

**Memory & Learning**
- Persistent memory of observations, decisions, and feedback
- Learned rules that improve over time (with your corrections)
- Semantic search across all captured data
- Automatic pruning of stale information via memory decay

## How It Works

```
Your Digital Life
    ↓
(Email, Calendar, Notes, Obligations)
    ↓
Auto-capture hooks
    ↓
Privacy filter (redaction of sensitive data)
    ↓
Observation database (SQLite)
    ↓
[Memory consolidation] → [Semantic search] → [Contradiction detection]
    ↓
Backend executor (Ollama/MLX/Claude)
    ↓
Suggested actions (drafts, categories, alerts)
    ↓
Your approval/feedback
    ↓
Learning rules database
    ↓
Next time, better suggestions
```

## Quick Start

**Time required:** 60 minutes setup, then 5 minutes/day ongoing

1. **Install**
   ```bash
   pip install -r install/requirements.txt
   ```

2. **Configure**
   - Edit `config/dcos_config.yaml` with your preferences
   - Set up your Gmail OAuth credentials
   - Specify your Obsidian vault location

3. **Run**
   ```bash
   python main.py
   ```

4. **Review**
   - Check daily digest
   - Approve/reject suggestions
   - Provide feedback on mistakes

Full instructions: see `QUICKSTART.md`

## What's Included

```
digital-chief-of-staff/
├── README.md              ← You are here
├── QUICKSTART.md          ← Get running in 60 minutes
├── CREDITS.md             ← Acknowledgments and sources
│
├── main.py                ← Run this to start dCoS
├── config/
│   └── dcos_config.yaml   ← Configure everything here
│
├── modules/               ← All dCoS functionality (15 modules)
│   ├── Core Modules:
│   │   ├── backend_executor.py
│   │   ├── vault_indexing.py
│   │   ├── account_manager.py
│   │   ├── learning_rules.py
│   │   ├── predictive_planning.py
│   │   ├── relationship_intelligence.py
│   │   ├── gmail_integration.py
│   │   ├── calendar_integration.py
│   │   └── obligation_manager.py
│   │
│   └── Memory Modules:
│       ├── embedding_provider.py
│       ├── memory_decay.py
│       ├── vector_search.py
│       ├── observation_capture.py
│       ├── contradiction_detector.py
│       └── privacy_filter.py
│
├── schema/                ← Database structure
│   ├── dcos_schema.sql
│   └── memory_extensions.sql
│
├── install/
│   └── requirements.txt
│
├── examples/              ← Sample configurations
│   └── minimal_config.yaml
│
└── docs/                  ← Detailed documentation
    ├── ARCHITECTURE.md
    ├── CONFIGURATION.md
    ├── FEATURES.md
    └── FAQ.md
```

## Key Features

- **Privacy First** — Everything runs locally. No data sent to cloud unless you explicitly choose a cloud backend
- **Transparent** — All suggestions are drafted. You see and approve before anything happens
- **Learnable** — System improves from your corrections (300+ examples @ 95%+ accuracy to unlock autonomy)
- **Extensible** — Add new modules, integrate other tools, customize backends
- **Non-destructive** — All data is captured as observations. Nothing is deleted automatically
- **Offline-capable** — Works without internet if using local LLM (Ollama/MLX)

## System Requirements

- **Python:** 3.8 or later
- **Storage:** 500 MB for Obsidian vault sync, 1 GB for full history
- **LLM Backend:** 
  - **Ollama** (recommended) — 8 GB RAM, any CPU
  - **MLX** (Apple Silicon only) — 16 GB RAM minimum
  - **Claude API** — Cloud, no local compute needed
- **Accounts:** Gmail (primary + optional agent account), Google Calendar

## Architecture

dCoS has three core layers:

1. **Capture Layer** — Auto-capture hooks from email, calendar, vault, obligations
2. **Memory Layer** — Observations stored with decay, consolidations, learned rules
3. **Execution Layer** — Backend executor makes decisions, suggests actions

Each layer is modular and can be extended independently.

## Next Steps

- **Installation & Setup:** Read `QUICKSTART.md`
- **Configuration Reference:** See `docs/CONFIGURATION.md`
- **Detailed Features:** See `docs/FEATURES.md`
- **System Architecture:** See `docs/ARCHITECTURE.md`
- **Troubleshooting:** See `docs/FAQ.md`

## Support

If something isn't working:
1. Check `docs/FAQ.md` for common issues
2. Review your configuration in `config/dcos_config.yaml`
3. Check that all dependencies installed: `pip install -r install/requirements.txt`
4. Verify your database initialized: `python main.py --init-db`

## License & Credits

See `CREDITS.md` for detailed attribution and inspiration sources.

---

**dCoS: Your personal AI decision support system.**
