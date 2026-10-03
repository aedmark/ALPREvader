# Roadmap

Item IDs are permanent: `P<phase>-<nn>`. Never renumber; append new items at the end of their phase.
`[ ]` open · `[~]` in progress (who holds it, since when, and what is left) · `[x]` done · `[-]` dropped (say why,
and the decision). An item held `[~]` by someone else is theirs until they or a maintainer release it.

A finished item says what was done, the decision if any, the evidence (the test, or the measurement), and the date.
A new item says where it came from (a test run, a real user, a maintainer) and the date. Keep an item's history in it:
"tried X, measured Y, then did Z" is how the next session avoids trying X again. Bugs are items too, filed under
the phase they belong to.

## Phase 1: Reproducible setup

Goal: a fresh clone reaches a working route by following the README, with no undocumented manual steps.

- [ ] P1-01 Create the `alpr_cameras` schema (`node_id` primary key, `location`, `capture_zone`, GiST index) from
  the repo, e.g. a `db/init.sql` mounted into the PostGIS init directory. Nothing in the repo creates it today; the
  ingester's `ON CONFLICT (node_id)` needs the unique key. Done when a fresh `pgdata` volume ingests without manual
  SQL. (Found in the template adoption review, 2026-10-03.)
- [ ] P1-02 Add the missing GraphHopper `car.json` custom model referenced by `config-alpr.yml`, or switch to a
  bundled one. Done when `routing` starts from a fresh clone. (Adoption review, 2026-10-03.)
- [ ] P1-03 Document or automate fetching `graphhopper-web-9.1.jar` (gitignored, never downloaded by any script).
  (Adoption review, 2026-10-03.)
- [ ] P1-04 Make re-ingest replace stale cameras: `ON CONFLICT DO NOTHING` keeps moved/removed cameras forever, and
  switching states keeps the previous state's cameras. Decided: replace per source extract, keep other states (D-008).
- [ ] P1-05 `scripts/setup-usa.sh` downloads the USA map but does not point `config-alpr.yml` at it or ingest
  cameras; align it with `ingest_state.sh`.

## Phase 2: Privacy correctness

Goal: the "nothing leaves your machine" claim in the README is true.

- [ ] P2-01 Stop sending typed addresses to `nominatim.openstreetmap.org` from `index.html`; pick points by map click (D-007). Done when the
  page makes no request carrying origin/destination to a third-party host, checked in browser dev tools.
- [ ] P2-02 Serve Leaflet locally instead of from unpkg.com, and decide on map tiles (tile requests reveal the area
  viewed). Done when the UI works with the network unplugged after ingest, or the README states the exception.
- [ ] P2-03 Stop logging raw origin/destination coordinates at INFO in `main.py` (`get_evasive_route`).
- [ ] P2-04 Restrict CORS: `allow_origins=["*"]` with `allow_credentials=True` lets any site a user visits query
  the local API.

## Phase 3: Routing quality

- [ ] P3-01 Capture Zone radius is applied twice: ingest stores a 50 m buffer, then the API buffers it another 50 m,
  giving ~100 m. Make it 75 m (D-009) in a single setting; update README and UI text.
- [ ] P3-02 `cameras_evaded` reports cameras in the padded bounding box, not cameras the route avoided. Compute it
  by intersecting the returned line with the zones, and also report cameras the route still passes.
- [ ] P3-03 Docstring of `build_custom_graphhopper_payload` says priority ×0.0; code uses ×0.01 (D-003). Fix the doc.
- [ ] P3-04 Support the `profile` field honestly: only `car` is configured; reject other values with 400.
- [ ] P3-05 Return a clear error when origin or destination lies inside a Capture Zone.

## Phase 4: Quality: tests, tooling, robustness

- [ ] P4-01 Offline unit tests for `build_custom_graphhopper_payload` and request validation (pytest, no DB or
  GraphHopper). Then a CI job running them plus `tools/check_docs.py`.
- [ ] P4-02 Add a linter/formatter (ruff) to `pyproject.toml` and the fast checks.
- [ ] P4-03 Integration test against a tiny fixture `.osm.pbf` with a known camera, run in Docker.
- [ ] P4-04 Validate coordinate ranges (lon ±180, lat ±90) and cap bounding-box size on `/api/v1/cameras/bbox`.
- [ ] P4-05 Lower the default `JAVA_OPTS` heap or document per-state sizing; 24 GB fails on most laptops.

## Phase 5: Later / only if wanted

Not committed. Decide only after the phases above ship.

- [ ] P5-01 Multiple states at once (merged extracts) without the whole-USA RAM cost.
- [ ] P5-02 User-supplied private camera list, kept out of the repo.
- [ ] P5-03 Adjustable avoidance strength / radius in the UI.

## Phase 6: Non-code items

- [ ] P6-01 Rename the package in `pyproject.toml` from `pythonproject` to `alpr-evader`.
- [ ] P6-02 Choose a version scheme and start the changelog's first release.
- [~] P6-03 Security contact (D-010; Claude, since 2026-10-03). Documented in SECURITY.md; left: a maintainer
  enables private vulnerability reporting in the GitHub repo settings.
