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

_Last updated: 2026-10-07, session 2, on `feature/3x-documentation` (from `63aba84`): 3x manual source,
generated HTML, generator, validation, and supporting docs added but not committed. No runtime code changed._

**Where things stand, in one paragraph:** The stack (PostGIS + GraphHopper + FastAPI + Leaflet) exists and, per the
maintainers, routes around cameras on their machines. A fresh clone cannot reproduce that yet: the database schema,
GraphHopper's `car.json`, and the jar are not in the repo (Phase 1). The biggest gap is the privacy promise: the UI
sends typed addresses to a public geocoder (Phase 2). There are no automated tests.

**Verified** (2026-10-07, on `63aba84` + uncommitted documentation, CachyOS Linux, Python 3.14.7)

| Suite | Result |
| --- | --- |
| `python3 tools/check_docs.py` | **0 errors** |
| `python3 tools/3x_manual.py check docs/manual/alpr-evader.manual.json` | **5 sections, 21 entries, 0 warnings** |
| `python3 -m py_compile main.py scripts/ingest_state.py tools/3x_manual.py tools/check_docs.py` | **pass** |
| 3x manual browser QA | **pass** at 1280 px and 390 px; search, empty state, anchors, and console checked |

**What works** (from maintainers' README; not re-run this session)
- **Evasive routing** (D-002, D-003; `main.py`). Car routes that avoid Capture Zones where an alternative exists.
- **State ingest** (`scripts/ingest_state.sh`). One US state at a time from Geofabrik.
- **3x project manual** (`docs/manual/index.html`). Standalone searchable synthesis of behavior, operation,
  architecture, trade-offs, and known limitations (D-011).

**Not verified**
- Nothing has been run end to end this session: no Docker, no map data in the checkout.
- A fresh-clone install has never been recorded working.

**Gotchas for the next session**
- `graph-cache/` is created root-owned by the container; delete it only via the script's Docker trick.
- Default `JAVA_OPTS` reserves 24 GB at start.
- Commit messages before this session are mostly "3"; history carries little intent.
- `3x-documentation-scheme/` is the untracked nested template checkout supplied for session 2. It was left intact;
  do not add it wholesale because it contains its own `.git`, IDE settings, and generated caches.

## Next steps (in order)

1. Maintainer: review and merge `feature/3x-documentation`; enable GitHub private vulnerability reporting (P6-03).
2. P1-01 schema in repo, then P1-02 and P1-03, so a fresh clone works.
3. P2-01 to P2-03: make the privacy claim true.
4. P4-01: first pytest suite for the payload builder, so Phase 3 changes have a safety net.

## Open questions for maintainers

None open. Q-001 to Q-005 answered 2026-10-03 (D-006 to D-010).

## Session log

Newest first. Copy the template for each new session. Work done between sessions (a maintainer's commits, another
agent) gets a short entry too, written by whoever notices it, so the log has no gaps. Past 10 entries, move the
oldest to `docs/archive/` and leave a pointer here.

### Session 2: 2026-10-07: apply the 3x documentation scheme

**Contributor:** Codex
**Goal:** Apply the supplied 3x documentation template to ALPR Evader as a maintainable project manual.
**Done:** none (documentation-only work without a roadmap item)
**Changed:** added a 21-entry manual source, schema, MIT attribution, generated standalone HTML, and the
standard-library generator; linked the manual from README and the documentation map; made `check_docs.py` validate
the source and reject stale output; recorded D-011 and the changelog entry. No runtime behavior changed.
**Decisions:** D-011 keeps the existing purpose-specific documents authoritative and treats the 3x manual as a
generated synthesis.
**Verified:** 3x check: 5 sections, 21 entries, 0 warnings; `tools/check_docs.py`: 0 errors, 0 warnings; `py_compile`
pass for application and documentation tools; browser QA passed at 1280 px and 390 px with search, empty state,
anchors, overflow, and console checked.
**Not verified:** the running Docker stack and manual route check; this change does not affect them.
**Problems / surprises:** desktop browser QA exposed horizontal overflow from the content flex minimum; added
`min-width: 0` to the generated layout and rechecked. The IDE independently added a nested-repository mapping to
`.idea/vcs.xml`; it is unrelated and was left untouched.
**Corrections:** the old handoff still described `feature/agent-workflow` as unmerged, but `main` now contains that
work at `63aba84`; current branch and next steps were updated.
**Left undone:** changes are not committed. The supplied `3x-documentation-scheme/` checkout remains untracked and
is not part of the integration.
**Next session should start with:** review this diff and commit it if accepted, then continue P1-01.

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
