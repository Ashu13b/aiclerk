# AGENT_KNOWLEDGE

Hand-written, agent-maintained. The maps say *what exists*; this says *why*.
None of it is auto-derivable — keep it current as you learn.

## Intent
Why this project exists; current goals.

## Execution context
Where the code actually runs (local / server / container / cron / API), and what
triggers it.

## State
What lives in the DB / cache / files, and what each piece means. Describe it —
never paste live contents.

## Decisions & rejected approaches
- **Search implementation**: We chose a hybrid SQLite setup. Since precompiled `sqlite-vss` wheels do not exist for Linux AArch64, we implemented a dynamic loading check. If `sqlite_vss` is importable, it loads the C extension. If not, it registers a custom Python-based `cosine_similarity` function into the SQLite connection. This maintains full SQL-level query capabilities (e.g. `ORDER BY cosine_similarity(...) DESC`) on all architectures.
- **Embedding Fallback**: If generating query embeddings fails (due to internet connectivity or provider configurations), the search seamlessly falls back to standard SQL text substring searching over the `search_content` field.

## Half-done / known-broken
None. Semantic search and REPL command execution are fully tested and functional.
