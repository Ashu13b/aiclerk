# ROADMAP

Hand-written, agent-maintained. The maps say *what exists now*; this says *what's
shipped, what's next, and what's deliberately out of scope*. Not auto-derivable —
keep it current as scope changes, and prefer a commit/PR ref over prose.

## Shipped
- Semantic Search: `aiclerk find <query>` using SQLite and cosine similarity with embedding/text search fallback.
- Interactive REPL: Fixed Click subcommand context parsing so parameterized commands execute correctly inside `/` shell.
- DocClerk Mobile-Web UI: Full React Native (Expo) dashboard with Vault Overview, Inbox Proposals, Form Filling, Semantic Search Screen, and Settings Panel.

## Next
- Real-time Notifications: Background agent alerts.

## Out of scope
What was considered and deliberately deferred or rejected — so it isn't re-proposed.
