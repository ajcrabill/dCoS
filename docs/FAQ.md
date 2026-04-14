# Frequently Asked Questions

## Installation & Setup

**Q: Do I need a Gmail account?**
A: Yes, primary Gmail for reading email. Optionally a second account for dCoS to use for drafts.

**Q: Can I use with Outlook or other email?**
A: Currently only Gmail. Outlook support coming later.

**Q: What if I don't have Obsidian?**
A: It's optional but recommended. Download from https://obsidian.md

**Q: I got "module not found" error**
A: Run: `pip install -r install/requirements.txt`

**Q: How do I set up Gmail OAuth?**
A: See QUICKSTART.md "Gmail OAuth Setup" section (15 minutes)

**Q: Can I run dCoS on a server?**
A: Yes, with headless setup. Contact support for details.

---

## Configuration

**Q: What's the difference between the three autonomy levels?**
A: 
- **Conservative:** You approve every action (safest for learning)
- **Balanced:** dCoS handles low-risk items, drafts uncertain ones
- **Aggressive:** Mostly automatic, alerts you on exceptions

**Q: How do I switch backends (Ollama → Claude)?**
A: Edit `config/dcos_config.yaml`, change `executor_backend: "claude"`, restart

**Q: Can I use both Ollama and Claude?**
A: Yes. Set both as `enabled: true`, choose default in `backend_defaults`

**Q: What's the privacy strictness setting do?**
A: Controls how much sensitive data gets masked before storage
- **Strict:** Masks everything (slowest)
- **Balanced:** Masks API keys, passwords, etc (recommended)
- **Permissive:** Minimal masking (fastest)

**Q: I need absolute paths for vault location?**
A: Yes. Use `/Users/yourname/Documents/Vault` not `~/Vault`

---

## Running dCoS

**Q: How do I start dCoS?**
A: `python main.py`

**Q: How do I stop it?**
A: Press Ctrl+C

**Q: Can I run it in background?**
A: Yes: `python main.py &` or use screen/tmux

**Q: Does it use my computer's resources?**
A: Yes, if using Ollama/MLX. Plan on 2-5% CPU when idle, more during decisions

**Q: Will it slow down my computer?**
A: Minimal impact. Runs in background, uses low resources.

**Q: Can I close my laptop?**
A: If running locally, yes. If on a server, leave it running.

---

## Email & Calendar

**Q: Why isn't dCoS seeing my emails?**
A: Check:
1. Gmail OAuth credentials configured
2. Credentials file at `config/gmail_credentials.json`
3. Gmail account has "Less secure" access enabled (if not using OAuth)

**Q: Can dCoS actually send emails?**
A: No. It only drafts. You review and send.

**Q: Does it read ALL my emails?**
A: Yes, back to when OAuth authorized (usually all history)

**Q: Can it handle multiple Gmail accounts?**
A: Currently only one primary account

**Q: How does it know what's "urgent"?**
A: Learns from your feedback. Initially looks for keywords, sender patterns

---

## Learning & Improvement

**Q: How long until dCoS gets good?**
A: Improves immediately, but:
- Week 1: Understands basic patterns
- Week 2-3: Noticeable improvement
- Month 1: Good baseline accuracy
- Month 3+: Excellent when you provide feedback

**Q: How do I give feedback?**
A: Click "helpful" or "not helpful" on suggestions. Edit drafts to show preferred style.

**Q: Can I correct learned rules?**
A: Yes, with feedback. dCoS updates confidence based on your corrections

**Q: What's the "300+ examples" rule about?**
A: After 300+ correct examples at 95%+ accuracy, you unlock next autonomy level

**Q: Can I see what dCoS learned about me?**
A: Yes, view learned_rules table in database using SQLite browser

**Q: Can I delete learned rules?**
A: Yes, but better to correct them with feedback

---

## Privacy & Data

**Q: Where is my data stored?**
A: Local SQLite database at `./state/chief_of_staff.sqlite` (you can backup/move anytime)

**Q: Is my data encrypted?**
A: SQLite itself is not. Use SQLite encryption tool for additional security.

**Q: Can I backup my data?**
A: Yes. Copy `state/chief_of_staff.sqlite`. It's a standard SQLite file.

**Q: Can I export data?**
A: Yes. Use SQLite tools: `SELECT * FROM observations;` etc

**Q: What data goes to the cloud?**
A: Only if using Claude backend. Queries sent, responses received. No storage on Claude side.

**Q: Can I delete observations?**
A: Yes, with direct database access. Or they fade via memory decay.

**Q: Does dCoS spy on me?**
A: No. It only sees what you allow (emails, calendar, vault). No telemetry.

---

## Performance

**Q: Why is it slow?**
A: Usually backend. Check:
- Ollama: Is it running? `ollama serve`
- Claude: Do you have internet?
- Database: Very large database (100k+ observations) slows search

**Q: How can I speed it up?**
A: 
- Use MLX if you have Apple Silicon
- Run Ollama in GPU mode
- Switch to Claude if you want cloud speed
- Clean old observations (memory decay helps)

**Q: How much storage does it use?**
A: ~5MB per 1000 observations. Most people: 500MB-2GB total

**Q: Should I worry about database size?**
A: No. Memory decay automatically prunes old data.

---

## Errors & Troubleshooting

**Q: "Cannot connect to Ollama"**
A: 
1. Is Ollama installed? https://ollama.ai
2. Is it running? `ollama serve`
3. Check endpoint: `http://localhost:11434`
4. Test: `curl http://localhost:11434/api/tags`

**Q: "Database is locked"**
A: 
- dCoS is already running somewhere else
- Check: `ps aux | grep main.py`
- Kill any existing process, restart

**Q: "Vault path not found"**
A:
- Use absolute path: `/Users/yourname/Documents/Obsidian Vault`
- Not relative: `~/Documents/Obsidian Vault`
- Path must exist before starting dCoS

**Q: "CLAUDE_API_KEY not found"**
A: `export CLAUDE_API_KEY="sk-..."`

**Q: Suggestions are terrible/random**
A:
- Just starting? Needs 50+ observations first
- Check autonomy level (should be conservative to start)
- Provide feedback (helpful/not helpful)
- Check backend is working: `python main.py --test`

**Q: Nothing is being captured**
A:
- Check Gmail OAuth: `ls config/gmail_credentials.json`
- Check vault path: Can dCoS access it? `ls /path/to/vault`
- Check database exists: `ls state/chief_of_staff.sqlite`
- Run: `python main.py --test`

**Q: Getting "Permission denied" errors**
A:
- Check file permissions: `ls -la`
- Check directory access: `mkdir -p state` if needed
- Run with appropriate user

---

## Advanced

**Q: Can I see dCoS's decision reasoning?**
A: Yes, from prompts sent to backend (logged in debug mode)

**Q: Can I use a different LLM?**
A: Only ones configured. Could add new backends (see module structure)

**Q: Can I customize email categories?**
A: Yes, in config. Add/remove as needed.

**Q: Can I write custom prompts?**
A: Yes, backend_executor module has prompts you can edit

**Q: Can I run multiple instances?**
A: Not recommended (database locking). Use one primary instance.

---

## Support

Still have questions?
1. Check README.md for overview
2. See QUICKSTART.md for setup
3. Check ARCHITECTURE.md for how it works
4. See CONFIGURATION.md for all options

---

**Last updated:** 2024
