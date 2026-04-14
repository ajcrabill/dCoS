# Features Guide

What dCoS can do for you.

## Email Management

**Triage**
- Automatically categorizes incoming email
- Suggests labels based on your patterns
- Flags urgent messages from VIPs
- Tracks follow-ups

**Draft Assistance**
- Suggests replies based on context and your communication style
- Mimics tone of original sender
- Proposes subject lines
- Never sends without approval

**Obligation Capture**
- Extracts tasks and deadlines from email
- Links emails to obligations for context
- Tracks who asked for what
- Reminds before deadlines

## Calendar Intelligence

**Schedule Optimization**
- Flags back-to-back meetings
- Suggests deep work time blocks
- Identifies meeting-free periods
- Recommends optimal meeting times

**Conflict Detection**
- Alerts on overlapping meetings
- Identifies scheduling patterns (e.g., "you always end meetings late")
- Flags impossible schedules
- Suggests rescheduling

**Context Aggregation**
- Summarizes attendees and their context
- Pulls relevant recent interactions
- Flags if meeting is with VIP
- Provides preparation notes

## Obligation Management

**Task Tracking**
- Captures obligations from email, calendar, and notes
- Links tasks to context (who, what, when, why)
- Tracks dependencies
- Monitors deadline progression

**Priority Intelligence**
- Learns your priority patterns
- Suggests task order
- Identifies blocked tasks
- Recommends what to do next

**Aging Analysis**
- Highlights tasks that haven't progressed
- Flags tasks approaching deadline
- Shows stuck obligations
- Suggests re-negotiation or escalation

## Relationship Management

**Contact Intelligence**
- Tracks when you last contacted someone
- Remembers context of interactions
- Flags VIPs you haven't contacted recently
- Suggests outreach timing

**Relationship Context**
- Remembers key details about people
- Tracks relationship type (boss, peer, report, client)
- Suggests communication frequency
- Learns your relationship patterns

**Network Intelligence**
- Identifies clusters of related people
- Tracks who introduced you to whom
- Suggests collaborative opportunities
- Reminds of birthday/anniversary

## Learning & Adaptation

**Pattern Recognition**
- Learns your email categories from examples
- Understands your priority system
- Recognizes urgent signals (specific words, senders)
- Adapts to your communication style

**Confidence Scoring**
- Each learned rule has a confidence score (0-100%)
- Score increases with correct applications
- Score decreases if contradicted
- Only uses high-confidence rules for autonomous action

**Feedback Loop**
- You approve/reject each suggestion
- System learns from your feedback
- Incorrect categorizations get corrected
- Rules improve over time

**300+ Example Rule**
- After 300+ correct examples at 95%+ accuracy
- Autonomy level unlocks to next tier
- Example: "Draft all" → "Draft important" → "Auto-categorize"

## Memory & Search

**Semantic Search**
- Search by meaning, not just keywords
- Examples:
  - "Who haven I talked to recently?"
  - "What's my pattern with this client?"
  - "When did Sarah mention the launch date?"
  - "Who typically responds quickly to emails?"

**Persistent Observation**
- All observations stored permanently
- Nothing auto-deleted (only memory decay)
- Full audit trail of what you've done
- Historical patterns visible

**Memory Decay**
- Old memories fade gradually (Ebbinghaus curve)
- Half-life: 30 days (configurable)
- Recent memories weighted more heavily
- Old routine patterns naturally forgotten

**Contradiction Detection**
- System flags when observations conflict with learned rules
- Example: "You usually email this client by Tuesday, but it's Wednesday"
- Triggers review of the rule
- Learns that patterns sometimes change

## Privacy & Control

**Data Redaction**
- Automatic masking of sensitive data before storage
- Patterns masked: API keys, passwords, SSNs, credit cards, PHI
- Redaction level: strict, balanced, or permissive
- Redacted data not recoverable from database

**Offline Capability**
- Works completely offline with Ollama or MLX
- No data leaves your machine unless configured
- Cloud backends (Claude) are optional
- All local processing available

**Access Control**
- Single user per installation
- OAuth credentials stored locally
- No account creation required
- No cloud synchronization

**Data Ownership**
- All data remains on your computer
- Database is standard SQLite (portable)
- Can export observations anytime
- Can delete data anytime

## Customization

**Backend Selection**
- Ollama (local, free, privacy)
- MLX (Apple Silicon, fast, free)
- Claude (cloud, best quality)
- Mix and match for different tasks

**Triage Modes**
- Draft all (conservative, safest)
- Draft important (balanced)
- Smart label (aggressive, requires high confidence)

**Autonomy Levels**
- Conservative (draft everything)
- Balanced (auto-handle low-risk, draft uncertain)
- Aggressive (auto-handle most, alert on exception)

**Privacy Levels**
- Strict (maximum redaction)
- Balanced (common redaction)
- Permissive (minimal redaction)

## Reporting & Analysis

**Weekly Digest**
- Summary of suggestions made
- Accuracy metrics
- Rules applied successfully
- Patterns identified
- Time saved estimate

**Monthly Review**
- Trend analysis
- Most-applied rules
- Communication patterns
- Relationship health check
- Obstacle identification

**Custom Queries**
- SQL access to database
- Export observations
- Analyze patterns
- Build custom reports

---

See `CONFIGURATION.md` for how to enable/disable features.
