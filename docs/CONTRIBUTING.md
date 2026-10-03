# Contributing

Use this file for the workflow shared by human and automated contributors. Agent-specific standing instructions are
in [AGENTS.md](../AGENTS.md).

## Before changing code

1. Read the README, the relevant roadmap item, architecture section, and test guidance.
2. Follow the README Quick Start; see [TESTING.md](TESTING.md) for memory settings and the missing setup pieces
   (P1-01 to P1-03).
3. Check `git status` and confirm that your change will not overlap unrelated work.
4. For a large or irreversible change (schema, data wipe, new external host), agree on scope and rollback first.

## Make the change

- Keep each change reviewable and focused on one outcome.
- Keep the API contract in [ARCHITECTURE.md](ARCHITECTURE.md) compatible; `index.html` is its only client, so change
  both together when it must change.
- Add or update tests for changed behaviour once a suite exists (P4-01).
- Update documentation according to [the documentation triggers](README.md#update-triggers).
- Do not include credentials, real personal locations, map extracts, `graph-cache/`, or the GraphHopper jar.

## Verify

```bash
python3 tools/check_docs.py
python3 -m py_compile main.py scripts/ingest_state.py
```

Follow [TESTING.md](TESTING.md) for the manual route check. Report the exact checks run and any skipped.

## Submit and review

Branch `feature/<roadmap-id>-<topic>` from `main`; commit messages start with the roadmap ID when one applies
(`P2-01: Geocode locally`). A maintainer reviews and merges (D-006). No CI yet (P4-01).

A change is ready when its scope is clear, relevant checks pass, user and migration impact is described, sensitive
data is absent, and the documentation it invalidated has been updated.

## Compatibility and migrations

No compatibility promise before a first release. A change to the `alpr_cameras` schema must say whether users must
re-ingest, and give the command.

## Reporting security issues

Do not open a public issue for a suspected vulnerability or privacy leak. Follow [SECURITY.md](SECURITY.md).
