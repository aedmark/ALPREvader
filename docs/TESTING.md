# Testing

How to run every check, what each one proves, and what it cannot. Read this before claiming anything works.
The results themselves live in HANDOFF's "Current state"; this file is how to get them.

## The suites

There is no automated test suite yet (P4-01). What exists:

| Suite | File | Proves | Does not prove | Time, needs |
| --- | --- | --- | --- | --- |
| Docs | `tools/check_docs.py` | IDs, decisions, questions and links in the docs are consistent | that the docs are true | seconds, Python only |
| Syntax | `python3 -m py_compile` | Python files parse | imports resolve, anything runs | seconds |
| Manual route | see below | the full stack routes around a known camera | other states, edge cases | ~30 min first time, Docker, RAM |

**The fast set** (before every commit): `python3 tools/check_docs.py`,
`python3 -m py_compile main.py scripts/ingest_state.py`.
**The full set** (before merging behaviour changes): the fast set plus the manual route check.

**Expected results** live in HANDOFF's "Verified" table, with the date and commit they were measured on.

## Before any run

- **Clean state:** camera data persists in the `pgdata` volume across runs, including cameras from earlier states
  (P1-04). Do not run `docker compose down -v` to "clean" without permission: re-ingest needs a fresh download.
- **Resource caps:** `routing` reserves `-Xms24g` by default. On smaller machines set `JAVA_OPTS` lower (a small
  state such as Rhode Island or Delaware works with ~2 GB) before starting it.
- **Services it needs:** `db` (5432 inside the network), `routing` on 8989 (ready when its log shows the server
  started), `api` on 8000.

## Running each suite

### Docs

```bash
python3 tools/check_docs.py
```

- A pass is `0 error(s)` and exit 0. Warnings (stale handoff date, long session log) do not fail it.

### Manual route check

```bash
./scripts/ingest_state.sh rhode-island
docker compose up -d
```

- Wait for `routing` to finish importing (`docker logs -f alprevader-routing-1`).
- Open http://localhost:8000, pan to a red Capture Zone, and route between two points on opposite sides of it on the
  same road.
- A pass: the blue route bends around the zone, and the response's `cameras_evaded` is non-zero. Note that
  `cameras_evaded` does not prove the route avoided anything (P3-02); look at the map.
- Also check in browser dev tools which hosts were contacted (P2-01).

### Adding a check

- Put pytest tests under `tests/` (P4-01). Test `build_custom_graphhopper_payload` as a pure function; stub
  `fetch_intersecting_zones` and `requests.post` for endpoint tests rather than needing Docker.
- Assert on what happened (the payload, the status code), not on words in a message.
- Before trusting a new check, make it fail: undo the fix (only the fix) and run it.

## Change-to-check matrix

| Changed area | Minimum checks | Additional evidence |
| --- | --- | --- |
| Documentation only | `python3 tools/check_docs.py` | — |
| `main.py` logic | fast set | unit tests once P4-01 lands; manual route check |
| `index.html` | fast set | manual route check; dev-tools network list for new hosts |
| Ingest scripts, SQL, schema | fast set | ingest a small state into a fresh volume |
| Compose, Dockerfiles, `config-alpr.yml` | fast set | `docker compose build`; full manual route check |
| Privacy boundary (D-004) | fast set | network capture showing no third-party request carries location |

## Manual checks (before a release)

- Fresh clone on a machine without prior volumes: follow README Quick Start exactly; record every manual step needed.
- Route check in Firefox and a Chromium browser.

## Environment recipes

- Local Python: `uv sync` creates `.venv` from `pyproject.toml`. Pytest is not a dependency yet; for ad-hoc use
  `uv run --with pytest pytest`.
- Coding-agent sessions usually cannot run Docker or download maps: run the fast set and say the manual check was
  not run.

## Known pitfalls (already hit, already fixed: don't re-discover these)

- **A mutation check must break the fix, not the test.** Reverting a whole file can fail a test for an unrelated
  reason. Remove just the fix.
- **`graph-cache/` is root-owned** when GraphHopper writes it from the container; `ingest_state.sh` deletes it via a
  throwaway Docker container for that reason.
