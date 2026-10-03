# Decisions

Short, append-only record of choices that a future session might otherwise re-litigate. One entry per decision.
Newest at the bottom. To reverse a decision, add a new entry that supersedes it; the old one keeps its text and only
its status changes ("superseded by D-MMM"). An "Update, same session" note at the end of an entry is fine while it is
still on the working branch.

Record pre-existing choices too, the first time a session has to understand them ("status: accepted, recorded
YYYY-MM-DD"): the reason something is the way it is gets lost faster than the code.

Format:

```
## D-NNN Title  (YYYY-MM-DD, status: proposed | accepted | rejected | superseded by D-MMM)
**Context:** why this came up (the roadmap item, the bug, the measurement).
**Decision:** what we chose (numbered points if there are several).
**Alternatives:** what else was considered, and why not (one line each). Optional, but it is what stops the
re-litigation.
**Consequences:** what it costs or constrains; what was left out and why.
**Review trigger:** an event that should cause reconsideration. Optional.
```

---

## D-001 Self-hosted Docker Compose stack  (2026-07-22, status: accepted, recorded 2026-10-03)
**Context:** The product's premise is that no third party learns a user's route (README, "Philosophy").
**Decision:** Ship as a local Docker Compose stack (PostGIS, GraphHopper, FastAPI, static page); no hosted service.
**Alternatives:** Hosted service like FlockHopper: rejected, it requires sending coordinates to a server.
**Consequences:** Users need Docker and substantial RAM; every user re-downloads and rebuilds map data.

## D-002 Per-request GraphHopper custom model with CH disabled  (2026-07-22, status: accepted, recorded 2026-10-03)
**Context:** Cameras to avoid differ per request (only those near the route corridor).
**Decision:** The API sends Capture Zones as custom-model `areas` with priority rules, and sets `ch.disable: true`
so GraphHopper uses flexible routing.
**Alternatives:** Bake cameras into the graph at import: faster queries, but a camera change needs a full rebuild.
**Consequences:** Flexible routing is slower than CH; `profiles_lm` is empty, so long routes may be slow (unmeasured).

## D-003 Soft avoidance: priority ×0.01, not ×0  (2026-07-22, status: accepted, recorded 2026-10-03)
**Context:** Some destinations are reachable only through a Capture Zone.
**Decision:** Multiply priority by 0.01 inside zones, so a route passes through only when no alternative exists.
**Alternatives:** ×0 (hard block): no route at all when a zone is unavoidable.
**Consequences:** A returned route may still pass a camera; the API does not currently say so (P3-02).

## D-004 User location never leaves the machine  (2026-07-22, status: accepted, recorded 2026-10-03)
**Context:** README promises origins and destinations "never leave your machine".
**Decision:** This is a product invariant. New external hosts need a decision and a SECURITY.md row.
**Consequences:** The current UI violates it (Nominatim geocoding, unpkg, OSM tiles): P2-01, P2-02.

## D-005 Capture Zone radius of 50 m  (2026-07-22, status: superseded by D-009, recorded 2026-10-03)
**Context:** README states a 50-metre zone per camera.
**Decision:** 50 m around the camera point.
**Consequences:** The code currently applies it twice (~100 m effective): P3-01, Q-004.

## D-006 Feature branches, maintainer merges  (2026-10-03, status: accepted)
**Context:** Q-001. History shows direct commits to `main` with messages like "3"; the maintainers want healthier
git habits.
**Decision:** 1. All work happens on `feature/<roadmap-id>-<topic>` (or `feature/<topic>` when no item applies).
2. Commit messages are imperative and start with the roadmap ID when one applies. 3. Only a maintainer pushes and
merges to `main`; agents commit to a working branch when asked.
**Alternatives:** Direct-to-main: fast for two people, but leaves no review point and no readable history.
**Consequences:** Every change needs a branch and a merge step.

## D-007 Geocoding by map click; no third-party geocoder  (2026-10-03, status: accepted)
**Context:** Q-002; D-004 is violated by the Nominatim calls in `index.html`.
**Decision:** Origin and destination are picked by clicking the map (or typing coordinates). Typed-address search to
a public service is removed. A self-hosted geocoder container (Photon/Nominatim) may be added later as optional.
**Alternatives:** Keep public Nominatim with a warning: breaks the product's core promise.
**Consequences:** Less convenient input until a local geocoder exists.

## D-008 Re-ingest replaces that state's cameras; other states are kept  (2026-10-03, status: accepted)
**Context:** Q-003 (maintainer deferred to the agent). `ON CONFLICT DO NOTHING` keeps removed or moved cameras
forever; wiping everything on each ingest would lose other states' data.
**Decision:** Each camera row records its source extract (e.g. `iowa`). An ingest deletes and reinserts that source's
rows in one transaction; rows from other sources are untouched. A camera tagged in two overlapping extracts keeps
the most recent source.
**Alternatives:** Accumulate (current): stale cameras never leave. Wipe all: a state switch loses the others.
**Consequences:** Schema needs a `source` column (P1-01, P1-04). A failed ingest rolls back and leaves the old data.

## D-009 Capture Zone radius of 75 m, applied once  (2026-10-03, status: accepted)
**Context:** Q-004. D-005 documented 50 m; the code produces ~100 m by buffering twice.
**Decision:** 75 m around the camera point, defined in one setting and applied in exactly one place.
**Consequences:** README and UI text must say 75 m (P3-01). Supersedes D-005.

## D-010 Vulnerabilities reported via GitHub private reporting  (2026-10-03, status: accepted)
**Context:** Q-005. The maintainer answered that the user (the repository owner) receives reports.
**Decision:** Reports go to the repository owner through GitHub private vulnerability reporting on
`aedmark/ALPREvader`. No personal email address is published in the docs.
**Consequences:** A maintainer must enable private vulnerability reporting in the repository settings (P6-03).

## Open questions

Questions requiring maintainer or stakeholder input. This is their one home: HANDOFF and the roadmap refer to them by ID. Numbers are
permanent; an answered question stays, with the answer and its date.

```
- **Q-NNN** The question. (asked YYYY-MM-DD, by whom; blocks P1-NN; recommendation: ...)
- **Q-NNN** ~~The question.~~ Answered YYYY-MM-DD: the answer, D-NNN.
```

- **Q-001** ~~Branch workflow: keep direct-to-`main`, or feature branches merged by a maintainer?~~ Answered 2026-10-03: feature branches, maintainer merges, D-006.
- **Q-002** ~~Geocoding without a third party: self-hosted Photon/Nominatim container, or coordinate/map-click input
  only?~~ Answered 2026-10-03: map-click first, optional local geocoder later, D-007.
- **Q-003** ~~On re-ingest, replace a state's cameras or accumulate across states?~~ Answered 2026-10-03: replace per source extract, keep others, D-008.
- **Q-004** ~~Intended Capture Zone radius: 50 m as documented, or the ~100 m the code produces?~~ Answered 2026-10-03: 75 m, D-009.
- **Q-005** ~~Where should vulnerability reports go?~~ Answered 2026-10-03: repository owner via GitHub private reporting, D-010.
