# ALPR Evader

ALPR Evader is a self-hosted routing engine that plans driving routes around known Automatic License Plate Reader
(ALPR) cameras. It serves privacy-minded power users who run it on their own hardware. Technically it is a Docker
Compose stack: PostGIS holds camera locations extracted from OpenStreetMap, GraphHopper holds the road graph, a
FastAPI service (`main.py`) joins them, and a single-file Leaflet page (`index.html`) is the UI.

This is the canonical instruction file for coding agents. `CLAUDE.md` imports it; do not duplicate these rules in
tool-specific files. Project facts belong in the documents linked below, not in an agent's private memory.

## Start here

1. Read `docs/HANDOFF.md` for the current state, active work, and gotchas.
2. Read the relevant roadmap item and the parts of `docs/ARCHITECTURE.md` and `docs/TESTING.md` that apply.
3. Inspect `git status` and recent history. Do not overwrite work you did not create.
4. Verify important inherited claims before relying on them. Use the fastest relevant check first.
5. State the intended scope briefly, then work on one independently reviewable change at a time.

If the repository is new or unfamiliar, read `README.md` and `docs/README.md` first. If the request conflicts with
these instructions or the working tree contains overlapping edits, stop and ask the maintainer.

## While working

- Reference roadmap or issue IDs where one exists. Do not invent an ID for an incidental, self-contained fix.
- Keep changes scoped. Do not mix opportunistic refactors with requested work.
- Preserve user changes. Never reset, clean, or rewrite history without explicit permission.
- Record a decision in `docs/DECISIONS.md` when reasonable maintainers could revisit the choice later.
- Update documentation in the same change when behaviour, interfaces, commands, risks, or project structure change.
- Distinguish observed facts from inference. Include the command, date, environment, or source behind volatile claims.
- Prefer enforcement to prose: important invariants should have a test, type, schema, linter, or runtime check.
- Treat all external input as untrusted at its boundary. Never expose secrets in logs, fixtures, prompts, or commits.
- Add newly discovered work to `ROADMAP.md` only when it is genuinely out of scope for the current change.
- **Privacy is the product.** Any change that makes the browser or server contact a new third-party host, or logs a
  user's origin/destination, needs a decision in `docs/DECISIONS.md` and a row in `docs/SECURITY.md` first.

## Finishing a change

1. Run the checks appropriate to the change, following `docs/TESTING.md`. Record failures and anything not run.
2. Review the diff for unrelated edits, generated files, credentials, stale names, and documentation drift.
3. Update `docs/HANDOFF.md` if work will continue in another session or if the repository's current state changed.
4. Update the roadmap item, decision record, architecture, security notes, and changelog only when their documented
   update trigger applies (see `docs/README.md`).
5. Run `python3 tools/check_docs.py` and report the result.

Do not manufacture ceremony: typo-only or mechanical changes do not need a decision, changelog entry, or handoff
rewrite unless they alter a claim those documents make.

## Working agreement

Branch-based workflow (D-006). Earlier history (to 2026-07-22) was direct-to-`main`; do not continue that.

- Default branch: `main`.
- Working branch pattern: `feature/<roadmap-id>-<topic>` (e.g. `feature/P1-01-schema`), or `feature/<topic>` when
  no item applies; merged by a maintainer. Never commit directly to `main`.
- Commit format: imperative summary, roadmap ID first when one applies: `P1-01: Add alpr_cameras schema`.
- Release/version scheme: none yet; `pyproject.toml` `version` is the placeholder source of truth (P6-02).
- Agents may commit to a working branch when asked. Only a maintainer pushes, merges to `main`, adds a dependency,
  changes the Docker images, or drops/rebuilds the `pgdata` volume or `graph-cache/`.

Never force-push, rewrite shared history, publish, or rotate/delete production data without explicit permission.

## Maintainer preferences

Record durable preferences here so they survive agent and session changes. Keep temporary task instructions in the
task or handoff instead.

- **Writing:** plain, direct English. The README's "sovereignty" voice is for user-facing copy only; keep technical
  docs factual.
- **Code comments:** explain *why* (a penalty value, a padding size, a PostGIS quirk), not what the line does.
- **Asking vs. doing:** ask before downloading map data, starting containers that allocate large heaps, wiping
  `graph-cache/`, or touching the database volume.
- **Reporting:** lead with the result; list the exact commands run and what was not run.

## Protected areas

Things an agent must not change without explicit permission. Every rule includes its reason or decision.

| Path or thing | Rule | Why |
| --- | --- | --- |
| `LICENSE` | Do not edit | Maintainer-owned legal text |
| `pgdata` Docker volume | Do not drop or recreate | Holds ingested camera data; rebuild needs a full re-download (ARCHITECTURE, "State and caches") |
| `graph-cache/` | Do not delete except via `scripts/ingest_state.sh` with permission | Rebuild takes minutes to over an hour and large RAM |
| Third-party hosts in `index.html` | Do not add new ones | Privacy is the product (D-004) |

## Names and terms

| Canonical term | Meaning | Formerly / not to be confused with |
| --- | --- | --- |
| ALPR Evader | This project | "ALPR Evasion Routing API" (FastAPI title), `pythonproject` (pyproject name) |
| Capture Zone | Polygon around a camera that routes are penalised for entering | The camera point itself |
| Camera | OSM node tagged `man_made=surveillance` + `surveillance:type=ALPR` | General CCTV |
| Ingest | Download a state's `.osm.pbf` and load its cameras into PostGIS | Building the GraphHopper graph (a separate step) |
| Custom model | GraphHopper per-request rules (`areas` + `priority`) | GraphHopper profile files |

## Repository map

| Path | Purpose |
| --- | --- |
| `main.py` | FastAPI app: serves UI, `/api/v1/routes/evasive`, `/api/v1/cameras/bbox` |
| `index.html` | Leaflet UI, geocoding, route display (single file, no build) |
| `scripts/ingest_state.sh` | End-to-end state ingest and routing-engine switch |
| `scripts/ingest_state.py` | Extract ALPR nodes from a `.osm.pbf` into PostGIS |
| `scripts/setup-usa.sh` | Download whole-USA map data |
| `config-alpr.yml` | GraphHopper server config (map file, profiles) |
| `docker-compose.yml` | db, routing, ingester, api services |
| `Dockerfile` | API image |
| `Dockerfile.ingester` | Ingester image |
| `pyproject.toml` | Python dependencies |
| `AGENTS.md` | Canonical agent instructions |
| `ROADMAP.md` | Planned work with stable IDs |
| `docs/README.md` | Documentation map and update triggers |
| `docs/HANDOFF.md` | Current state, next steps, gotchas, and bounded session history |
| `docs/ARCHITECTURE.md` | Components, boundaries, invariants, state, and failure modes |
| `docs/DECISIONS.md` | Append-only architectural and product decisions; open questions |
| `docs/TESTING.md` | Test strategy, commands, limitations, and environment recipes |
| `docs/SECURITY.md` | Assets, trust boundaries, secret handling, and reporting |
| `docs/CONTRIBUTING.md` | Human and agent contribution workflow |
| `docs/CHANGELOG.md` | User-visible release notes |
| `docs/manual/` | 3x manual source, schema, attribution, and generated standalone HTML |
| `docs/archive/` | Historical material no longer current |
| `tools/check_docs.py` | Documentation consistency checks |
| `tools/3x_manual.py` | Validate and generate the searchable 3x project manual |

## Engineering conventions

- Python 3.11 (the Docker base image); local dev may use newer. Dependencies via `pyproject.toml`; `uv` is used
  locally (`uv.lock` is gitignored). No linter configured yet (P4-02).
- Supported: Linux/macOS hosts with Docker Compose. Non-targets: mobile, hosted multi-user deployment.
- Coordinates are `[lon, lat]` (GeoJSON order) everywhere in the API and database; SRID 4326 in storage.
- Invariant: a user's origin and destination are never sent to a host other than the local stack (currently broken,
  see ARCHITECTURE "Claims vs. code" and P2-01).
- New dependencies, Docker images, or external hosts need maintainer approval and an ARCHITECTURE row.
- Generated/large files (`*.osm.pbf`, `graph-cache/`, `graphhopper-web-*.jar`) are never committed.

## Environments

| Environment | Can access | Cannot access / caveats |
| --- | --- | --- |
| Local development | Docker, Geofabrik downloads, `uv` | Routing needs a downloaded jar + map + RAM (`JAVA_OPTS` defaults to 24 GB) |
| Coding-agent session | Repo files, `python3`, `uv` | Assume no running stack, no map data, no Docker permission unless the maintainer says so |
| CI | None configured | (P4-01) |

## Run and verify

- Setup: `./scripts/ingest_state.sh <state>` (needs `graphhopper-web-9.1.jar` in the repo root, and a schema: P1-01).
- Run: `docker compose up -d`, then open http://localhost:8000.
- Fast checks: `python3 tools/check_docs.py && python3 -m py_compile main.py scripts/ingest_state.py`.
- Full checks: fast checks plus the manual route check in `docs/TESTING.md`.
- Detailed test guidance: `docs/TESTING.md`.
