# Security

This document describes the project's security and privacy assumptions and reporting path. It is not a claim that
the project is vulnerability-free.

## Supported versions

| Version / branch | Security fixes |
| --- | --- |
| `main` | supported (no releases yet) |

## Report a vulnerability

Use GitHub private vulnerability reporting on https://github.com/aedmark/ALPREvader (Security tab, "Report a
vulnerability"); reports go to the repository owner (D-010). Do not open a public issue. Include affected commit,
impact, reproduction steps, and any workaround. Do not include real home/work addresses or other personal location data.

## Assets and boundaries

The main asset is the user's travel pattern: origins, destinations, and the areas they view.

| Asset or boundary | Sensitivity / threat | Protection and validation | Owner |
| --- | --- | --- | --- |
| Typed addresses / coordinates | Disclosure of where a user lives and goes | Must stay local (D-004, D-007). **Currently sent to nominatim.openstreetmap.org** (P2-01) | `index.html` |
| Map viewport | Tile and Leaflet CDN requests reveal area of interest and IP | Not protected (P2-02) | `index.html` |
| API logs | Origin/destination logged at INFO | Not protected (P2-03) | `main.py` |
| Local API | Any website the user visits can call it (CORS `*`) | Not protected (P2-04) | `main.py` |
| Database credentials | Default `postgres`/`password` in compose and code | Acceptable only while `db` publishes no port; never expose 5432 | `docker-compose.yml` |
| Request input | Oversized bbox, bad coordinates | Parameterised SQL; no size or range limits (P4-04) | `main.py` |
| Downloaded OSM data | Malformed or hostile PBF | Fetched over HTTPS from Geofabrik; values bound as SQL parameters | ingest scripts |

Architecture details belong in [ARCHITECTURE.md](ARCHITECTURE.md); this table records the security consequence.

## Secure development rules

- Keep credentials and real locations out of code, docs, logs, fixtures, and screenshots. Use public landmarks in
  examples.
- No new third-party host in the UI or API without a decision (D-004).
- Validate at trust boundaries; always use parameterised SQL.
- Explicit timeouts on outbound calls (GraphHopper uses 10 s).
- Do not publish the `db` port or bind the API beyond localhost in examples without a warning.

## Security verification

No automated security checks. The privacy invariant is verified manually with the browser network tab (TESTING,
"Manual route check"). Gap: nothing prevents a regression.

## Incident response

If a release is found to leak location data: document the affected commits, fix on `main`, and note it in the
changelog in user terms so users can judge their exposure.
