# Configuration Reference

Complete guide to `config/dcos_config.yaml`

## Executor Backends

Choose which LLM to use for decision-making.

### Ollama (Recommended)
```yaml
executor_backends:
  ollama:
    enabled: true
    endpoint: "http://localhost:11434"
    model: "mistral"
    temperature: 0.7
    max_tokens: 500
```

**Setup:**
```bash
# Install: https://ollama.ai
ollama pull mistral
ollama pull nomic-embed-text
ollama serve  # Keep running
```

**Best for:** Privacy, cost ($0), offline use  
**Speed:** 150-500ms per decision  
**Quality:** Good for most tasks

### MLX (Apple Silicon Only)
```yaml
executor_backends:
  mlx:
    enabled: true
    model: "mlx-community/Mistral-7B-Instruct-v0.1"
```

**Setup:**
```bash
pip install mlx mlx-lm
export MLX_GPU=1  # Use GPU
```

**Best for:** Apple Silicon Macs  
**Speed:** 50-150ms (fastest)  
**Cost:** Free

### Claude (Cloud)
```yaml
executor_backends:
  claude:
    enabled: true
    model: "claude-3-5-sonnet"
    api_key_env: "CLAUDE_API_KEY"
```

**Setup:**
```bash
# Get key from https://console.anthropic.com
export CLAUDE_API_KEY="sk-..."
```

**Best for:** Highest quality  
**Speed:** 1-3s  
**Cost:** ~$0.01-0.10/month (low volume)

## Embeddings

Vector embeddings for semantic search.

### Ollama Embeddings
```yaml
embeddings:
  ollama:
    enabled: true
    model: "nomic-embed-text"
```

**Setup:** Includes automatic with Ollama

### MLX Embeddings
```yaml
embeddings:
  mlx:
    enabled: true
    model: "bert-base-uncased"
```

**Setup:** `pip install transformers torch`

## Default Selection

```yaml
backend_defaults:
  llm: "ollama"           # Which backend to use
  embeddings: "ollama"    # For semantic search
```

## User Context

Your personal information.

```yaml
preferences_schema:
  user_context:
    user_name: "Your Name"
    role_title: "VP of Product"
    primary_email: "you@company.com"
    time_zone: "America/Los_Angeles"
    operating_values:
      - "Innovation"
      - "Transparency"
      - "Learning"
```

## Time Management

Deep work and meeting preferences.

```yaml
time_management:
  weekly_hours_to_protect: 10  # Hours of focused work needed
  
  deep_work_preferences:
    preferred_days: [1, 2, 3, 4, 5]  # Monday-Friday
    preferred_time: "09:00-11:00"      # Block time
    no_meetings_before: "09:00"
    no_back_to_back: true
```

## Email Preferences

How dCoS handles email.

```yaml
email_preferences:
  email_triage_mode: "draft_all"  # draft_all | draft_important | smart_label
  auto_categories:
    - "leads"
    - "invoices"
    - "action_required"
    - "fyi"
```

**Modes:**
- `draft_all` — Creates draft for every email (safest)
- `draft_important` — Only important emails (balanced)
- `smart_label` — Auto-categorize (requires high confidence)

## Calendar Preferences

Calendar handling.

```yaml
calendar_preferences:
  calendar_triage_enabled: true
  meeting_buffer_minutes: 15    # Break between meetings
  max_meetings_per_day: 6       # Limit per day
```

## Relationship Preferences

Who to track and how often.

```yaml
relationship_preferences:
  key_people:
    - "sarah@company.com"
    - "bob@company.com"
  
  contact_frequency_days:
    manager: 3        # Check in every 3 days
    direct_reports: 2 # 1-on-1s every 2 days
    peers: 5
    clients: 7
```

## Autonomy Preferences

How much dCoS should do independently.

```yaml
autonomy_preferences:
  autonomy_level: "conservative"  # conservative | balanced | aggressive
  failure_mode: "draft_only"       # draft_only | ask_first | just_do_it
```

**Levels:**
- `conservative` — Drafts everything, you approve all
- `balanced` — Auto-handles low-risk, drafts uncertain
- `aggressive` — Auto-handles most, alerts on exceptions

**Failure Mode:**
- `draft_only` — Always draft if uncertain
- `ask_first` — Ask before taking action
- `just_do_it` — Take action if confident enough

## Workflow Preferences

Digests and reviews.

```yaml
workflow_preferences:
  enable_daily_digest: true
  daily_digest_time: "08:00"      # When to send
  
  enable_weekly_review: true
  weekly_review_day: "Friday"
  weekly_review_time: "17:00"
```

## System Preferences

Where data lives and how dCoS behaves.

```yaml
system_preferences:
  vault_location: "/Users/you/Documents/Obsidian Vault"  # ABSOLUTE path required
  database_location: "./state/chief_of_staff.sqlite"
  executor_backend: "ollama"
  privacy_strictness: "balanced"  # strict | balanced | permissive
```

**Privacy Strictness:**
- `strict` — Redact everything possible (slow)
- `balanced` — Redact sensitive data (recommended)
- `permissive` — Minimal redaction (fastest, less private)

## Advanced Settings

Safety and learning controls.

```yaml
advanced_settings:
  never_autonomous_send_to:
    - "your.boss@company.com"
    - "@important-client.com"
  
  learning_rules_enabled: true
  vault_indexing_enabled: true
```

## Common Configurations

### Minimal Setup
```yaml
executor_backends:
  ollama: {enabled: true}

backend_defaults:
  llm: "ollama"

preferences_schema:
  user_context:
    user_name: "Your Name"
    primary_email: "you@example.com"
    time_zone: "America/Chicago"
  
  system_preferences:
    vault_location: "/Users/you/Documents/Obsidian Vault"
    executor_backend: "ollama"
```

### Privacy-First Setup
```yaml
executor_backends:
  ollama: {enabled: true}

preferences_schema:
  system_preferences:
    privacy_strictness: "strict"
    executor_backend: "ollama"  # Local, no cloud
```

### Cloud-First Setup
```yaml
executor_backends:
  claude:
    enabled: true
    api_key_env: "CLAUDE_API_KEY"

backend_defaults:
  llm: "claude"
```

### Power User Setup
```yaml
# All features enabled
# All backends configured
# See config/dcos_config.yaml for example
```

## Applying Changes

1. Edit `config/dcos_config.yaml`
2. Restart dCoS: `python main.py`
3. Changes take effect immediately

## Validating Config

Check syntax:
```bash
python -m yaml config/dcos_config.yaml
```

Test startup:
```bash
python main.py --test
```

---

See `FAQ.md` for common configuration issues.
