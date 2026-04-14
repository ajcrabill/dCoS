# Credits & Acknowledgments

**Digital Chief of Staff**  
Created by: AJ Crabill  
Repository: https://github.com/ajcrabill/dCoS  
License: MIT

---

## Inspiration & Sources

dCoS incorporates architectural patterns and design inspiration from several open-source projects and research.

## Key Inspirations

### AgentMemory
[https://github.com/rohitg00/agentmemory](https://github.com/rohitg00/agentmemory)

dCoS's memory architecture is inspired by AgentMemory's multi-tier approach. Specifically:

- **Observation consolidation** — Capturing raw observations and consolidating them into higher-level facts
- **Memory decay** — Using exponential decay curves (Ebbinghaus model) to age memories over time
- **Semantic search** — Combining BM25 keyword search with vector embeddings for hybrid search
- **Contradiction detection** — Flagging conflicts between observations and learned rules
- **Privacy-first design** — Redacting sensitive data before storage

Key AgentMemory patterns we adapted:
1. **Multi-tier memory** (observations → consolidations → rules)
2. **Confidence scoring** with Bayesian updates
3. **Hook-based auto-capture** from multiple data sources
4. **SQLite as primary store** for durability
5. **Local embeddings** for semantic understanding

We recommend exploring AgentMemory for ideas on extended memory architectures, particularly around:
- Extended tier hierarchies (4 tiers vs our 2)
- Advanced consolidation patterns
- Temporal reasoning about observations
- Multi-agent memory coordination

**Creator:** Rohit G  
**License:** Check AgentMemory repository for current license

---

## Core Technologies

**Python Ecosystem**
- google-auth-oauthlib — Gmail and Google Calendar integration
- markdown, frontmatter — Obsidian vault parsing
- sqlite3 — Primary data store
- numpy, scikit-learn — Vector operations and similarity

**LLM Backends**
- [Ollama](https://ollama.ai) — Local model inference
- [MLX](https://ml-explore.github.io/mlx/) — Apple Silicon optimization
- Anthropic Claude API — Cloud alternative
- Together.ai — Open source model hosting

**Research Foundations**
- Ebbinghaus forgetting curve — Memory decay model
- BM25 algorithm — Full-text search ranking
- Cosine similarity — Vector similarity
- Bayesian inference — Confidence updates

---

## Architecture Principles

dCoS's design philosophy draws from:

1. **Privacy by default** — Local processing, explicit cloud opt-in
2. **Transparency** — All suggestions drafted before action
3. **Human-in-the-loop** — Learning requires feedback
4. **Modularity** — Independent modules for each capability
5. **Non-destructive** — Observations never auto-deleted
6. **Extensibility** — Easy to add new sources and actions

---

## Open Source Philosophy

dCoS builds on the work of:
- The Python community
- Google for APIs and OAuth patterns
- Obsidian for vault structure inspiration
- Open source LLM initiatives (Ollama, MLX, open models)

We believe in transparent attribution and encourage you to explore the projects that inspired this work.

---

## Contributing

If you improve dCoS:
- Add new modules following the existing patterns
- Include documentation for new capabilities
- Maintain privacy-first principles
- Give credit where inspired by other work
- Share improvements back if possible

---

## Questions About Sources?

For detailed information on any architectural decision or pattern:
1. Check the docstrings in the specific module
2. See `docs/ARCHITECTURE.md` for system design
3. Check the research papers cited in comments
4. Review the GitHub links above

We're grateful for the ecosystem of open-source AI tools that made dCoS possible.

---

**dCoS: Built on the shoulders of giants.**
