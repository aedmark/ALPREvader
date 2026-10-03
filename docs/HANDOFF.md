# Session Handoff

Read this first when resuming unfinished work. Rewrite the top half whenever current state changes materially or work
pauses with context another session needs.
The session log below it is append-only history. "Current state" fits on a screen or two (about 80 lines);
what does not fit is history, and belongs in the session log.

Protocol: see [AGENTS.md](../AGENTS.md) (`CLAUDE.md` imports it). Plan: [ROADMAP.md](../ROADMAP.md).
Architecture: [ARCHITECTURE.md](ARCHITECTURE.md). Decisions: [DECISIONS.md](DECISIONS.md).
Tests: [TESTING.md](TESTING.md). Security: [SECURITY.md](SECURITY.md).
Changes: [CHANGELOG.md](CHANGELOG.md). Older sessions: [archive/](archive/README.md).

---

## Current state

_Last updated: 2026-10-03, session 1, on `feature/agent-workflow` (from `665230c`): agent workflow docs and
decisions D-006 to D-010, committed, not pushed or merged. No code changed._

**Where things stand, in one paragraph:** The stack (PostGIS + GraphHopper + FastAPI + Leaflet) exists and, per the
maintainers, routes around cameras on their machines. A fresh clone cannot reproduce that yet: the database schema,
GraphHopper's `car.json`, and the jar are not in the repo (Phase 1). The biggest gap is the privacy promise: the UI
sends typed addresses to a public geocoder (Phase 2). There are no automated tests.

**Verified** (2026-10-03, on `665230c` + uncommitted docs, CachyOS Linux, Python 3.14.7)

| Suite | Result |
| --- | --- |
| `python3 tools/check_docs.py` | **0 errors** |
| `python3 -m py_compile main.py scripts/ingest_state.py` | **pass** |

**What works** (from maintainers' README; not re-run this session)
- **Evasive routing** (D-002, D-003; `main.py`). Car routes that avoid Capture Zones where an alternative exists.
- **State ingest** (`scripts/ingest_state.sh`). One US state at a time from Geofabrik.

**Not verified**
- Nothing has been run end to end this session: no Docker, no map data in the checkout.
- A fresh-clone install has never been recorded working.

**Gotchas for the next session**
- `graph-cache/` is created root-owned by the container; delete it only via the script's Docker trick.
- Default `JAVA_OPTS` reserves 24 GB at start.
- Commit messages before this session are mostly "3"; history carries little intent.

## Next steps (in order)

1. Maintainer: review and merge `feature/agent-workflow`; enable GitHub private vulnerability reporting (P6-03).
2. P1-01 schema in repo, then P1-02 and P1-03, so a fresh clone works.
3. P2-01 to P2-03: make the privacy claim true.
4. P4-01: first pytest suite for the payload builder, so Phase 3 changes have a safety net.

## Open questions for maintainers

None open. Q-001 to Q-005 answered 2026-10-03 (D-006 to D-010).

## Session log

Newest first. Copy the template for each new session. Work done between sessions (a maintainer's commits, another
agent) gets a short entry too, written by whoever notices it, so the log has no gaps. Past 10 entries, move the
oldest to `docs/archive/` and leave a pointer here.

### Template

```
### Session N: YYYY-MM-DD: short title

**Contributor:** person or agent/tool
**Goal:**
**Done:** roadmap IDs
**Changed:** files / behaviour
**Decisions:** D-numbers added
**Verified:** tests and their counts; mutation results if performed; for runs that vary, the tally
**Not verified:** checks skipped or environments unavailable
**Problems / surprises:**
**Corrections:** earlier notes (here or in other docs) found wrong, and what was actually true
**Left undone:**
**Next session should start with:**
```

### Session 1: 2026-10-03: adopt the agent-project template

**Contributor:** Claude Code (Opus 5.5)
**Goal:** Set up the agent workflow from `the-hypervisor/agent-template`, describing the repo as it is.
**Done:** none (roadmap seeded)
**Changed:** added `AGENTS.md`, `CLAUDE.md`, `ROADMAP.md`, `docs/*`, `tools/check_docs.py`. No code changes.
**Decisions:** D-001 to D-005 recorded as pre-existing choices; D-006 to D-010 from maintainer answers.
**Verified:** `tools/check_docs.py` 0 errors; `py_compile` pass.
**Not verified:** the running stack.
**Problems / surprises:** schema, `car.json`, jar missing from repo; README privacy claim contradicted by
`index.html`; zone radius doubled. The template's `check_docs.py` looked for a "Layout" section that `AGENTS.md`
calls "Repository map", so path checks never ran; fixed in this copy.
**Corrections:** none.
**Left undone:** all roadmap items.
**Next session should start with:** P1-01 (schema with `source` column per D-008).
