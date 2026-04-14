# Quick Start Guide

Get dCoS running in 60 minutes.

## Prerequisites (5 minutes)

Before starting, have these ready:

- [ ] Python 3.8+ installed (`python3 --version`)
- [ ] Gmail account (your personal email)
- [ ] Google Calendar synced with your email
- [ ] Obsidian vault created (see path in Settings)
- [ ] 1 GB free disk space

### Optional: Local LLM Setup

dCoS can use **Ollama** (recommended, free) or **Claude API** (cloud, paid).

**For Ollama (recommended):**
```bash
# Install Ollama: https://ollama.ai
# Download recommended model:
ollama pull mistral
ollama pull nomic-embed-text

# Keep running in background:
ollama serve &
```

**For Claude API:**
```bash
# Get API key from https://console.anthropic.com
export CLAUDE_API_KEY="sk-..."
```

**For MLX (Apple Silicon only):**
```bash
pip install mlx mlx-lm
```

## Step-by-Step Installation

### 1. Install Python Dependencies (5 minutes)

```bash
cd digital-chief-of-staff
pip install -r install/requirements.txt
```

### 2. Initialize Database (2 minutes)

```bash
python main.py --init-db
```

This creates:
- `state/chief_of_staff.sqlite` — Main database
- Tables for observations, learned rules, consolidations, etc.

### 3. Configure dCoS (30 minutes)

**Edit `config/dcos_config.yaml`**

Start with these sections:

#### A. LLM Backend (2 minutes)

Find this section and set `enabled: true` for your choice:

```yaml
executor_backends:
  ollama:
    enabled: true    # ← Use this for local, free
```

or

```yaml
executor_backends:
  claude:
    enabled: true    # ← Use this for best quality
```

#### B. User Context (5 minutes)

Under `preferences_schema` → `user_context`:

```yaml
preferences_schema:
  user_context:
    user_name: "Your Name"
    role_title: "Your Job Title"
    primary_email: "you@example.com"
    time_zone: "America/Chicago"  # Your timezone
```

#### C. System Paths (3 minutes)

Under `system_preferences`:

```yaml
system_preferences:
  vault_location: "/Users/yourname/Documents/Obsidian Vault"
  database_location: "./state/chief_of_staff.sqlite"
  executor_backend: "ollama"  # or: mlx, claude
  privacy_strictness: "balanced"
```

**Important:** Use absolute paths for vault location.

#### D. Gmail OAuth Setup (15 minutes)

1. Go to https://console.cloud.google.com
2. Create a new project
3. Enable Gmail API and Google Calendar API
4. Create OAuth 2.0 credentials (Desktop app)
5. Download credentials JSON
6. Save to: `config/gmail_credentials.json`

Or use app-specific password if using your own Gmail account.

#### E. Workflow Preferences (5 minutes)

Optional but recommended:

```yaml
workflow_preferences:
  enable_daily_digest: true
  daily_digest_time: "08:00"
  enable_weekly_review: true
  weekly_review_day: "Friday"
  weekly_review_time: "17:00"
```

### 4. Test Installation (5 minutes)

```bash
# Check all modules load
python main.py --test

# Expected output:
# ✓ Modules loaded
# ✓ Database connected
# ✓ Embeddings available
# ✓ Gmail OAuth ready
# ✓ Obsidian vault accessible
```

### 5. Start dCoS (2 minutes)

```bash
python main.py
```

You should see:
```
Digital Chief of Staff starting...
✓ Database initialized
✓ Capture hooks registered
✓ Backend executor ready
✓ Listening for email/calendar updates

Press Ctrl+C to stop
```

## First 24 Hours

### Hour 1-2: Capture Phase
dCoS begins observing your email and calendar. No actions yet — just learning.

### Hour 3-8: Suggestion Phase
Check your email for daily digest. Review first suggestions:
- Email categorizations
- Calendar conflicts
- Obligation summaries

**Your job:** Accept or reject. Click "Helpful" or "Not helpful" on each.

### Hour 9-24: Learning Phase
dCoS learns from your feedback. Suggestions improve.

## Common First Week Tasks

**Day 1:**
- [ ] Installation complete
- [ ] Test run works
- [ ] Receiving daily digests

**Days 2-3:**
- [ ] Review 10+ suggestions
- [ ] Provide feedback on accuracy
- [ ] Adjust privacy settings if needed

**Days 4-7:**
- [ ] Review learned rules (in database)
- [ ] Adjust email categories
- [ ] Fine-tune calendar preferences

## Configuration Examples

**Minimal Setup (just the basics):**
See `examples/minimal_config.yaml`

**Power User Setup (all features enabled):**
See `examples/power_user_config.yaml`

## Next Steps

- **Detailed Configuration:** `docs/CONFIGURATION.md`
- **All Features Explained:** `docs/FEATURES.md`
- **System Architecture:** `docs/ARCHITECTURE.md`
- **Troubleshooting:** `docs/FAQ.md`

## Troubleshooting

**"Module not found" error:**
```bash
pip install -r install/requirements.txt
```

**"Cannot connect to Ollama":**
```bash
# Check Ollama is running
ollama serve

# Verify endpoint in config:
# executor_backends.ollama.endpoint: "http://localhost:11434"
```

**"Database error":**
```bash
# Reinitialize database
rm state/chief_of_staff.sqlite
python main.py --init-db
```

**"Vault path error":**
- Use absolute path (e.g., `/Users/yourname/Documents/Obsidian Vault`)
- Not relative path (e.g., `~/Obsidian Vault`)

**More issues?** See `docs/FAQ.md`

---

**You're all set. dCoS is learning about you now.**
