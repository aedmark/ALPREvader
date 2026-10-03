# Architecture

How ALPR Evader fits together, for a session that has never seen it. This is the map, not the territory: it names
the parts and the rules between them, and leaves the detail to the code. Update it when the shape changes (a
service, endpoint, table or script added, moved or merged), not for every change inside one.

Why things are this way lives in [DECISIONS.md](DECISIONS.md); this file says *what* is, and points there.

## The shape, in one paragraph

Offline, `scripts/ingest_state.sh` downloads a state's `.osm.pbf` from Geofabrik, runs `scripts/ingest_state.py` in
the `ingester` container to copy every ALPR node into PostGIS table `alpr_cameras` (point plus a buffer: 50 m today, 75 m per D-009), then
optionally points `config-alpr.yml` at the new map and restarts `routing`, which builds `graph-cache/`. At runtime the
browser loads `index.html` from the `api` service; typed addresses are geocoded by the page, then `POST
/api/v1/routes/evasive` sends `[lon, lat]` pairs. The API pads the origin/destination bounding box by 0.1°, selects
intersecting Capture Zones, turns them into a GraphHopper custom model (D-002, D-003), and returns GeoJSON plus turn
instructions. The page also calls `GET /api/v1/cameras/bbox` on every map move to draw zones.

## Code map

| Area | Where | Entry point | Talks to |
| --- | --- | --- | --- |
| API | `main.py` | `get_evasive_route()` | PostGIS (psycopg2), GraphHopper (HTTP) |
| Zone query | `main.py` | `fetch_intersecting_zones()` | PostGIS |
| Custom model | `main.py` | `build_custom_graphhopper_payload()` | pure function |
| UI | `index.html` | inline `<script>` | API, Nominatim, OSM tiles, unpkg |
| Camera ingest | `scripts/ingest_state.py` | `ALPRHandler.node()` | PostGIS |
| Ingest pipeline | `scripts/ingest_state.sh` | script | Geofabrik, Docker, `config-alpr.yml` |
| Routing engine | `config-alpr.yml` | GraphHopper 9.1 jar | `graph-cache/` |

## Interfaces and data flow

```text
Geofabrik .osm.pbf -> ingest_state.py -> alpr_cameras (PostGIS)
browser -> POST /api/v1/routes/evasive -> zone query -> custom model -> GraphHopper /route -> GeoJSON
```

| Interface | Producer | Consumer | Contract / compatibility |
| --- | --- | --- | --- |
| `POST /api/v1/routes/evasive` | `main.py` | `index.html` | `{origin:[lon,lat], destination:[lon,lat], profile}` → `RouteResponse`; 400 out of bounds, 500 DB, 502 engine |
| `GET /api/v1/cameras/bbox` | `main.py` | `index.html` | query `min_lon,min_lat,max_lon,max_lat` → GeoJSON FeatureCollection |
| `alpr_cameras` table | `ingest_state.py` | `main.py` | `node_id` unique, `location` point, `capture_zone` polygon, SRID 4326. Schema not in repo (P1-01) |
| GraphHopper `/route` | GraphHopper 9.1 | `main.py` | custom model `areas` + `priority`; `ch.disable` |

## Invariants

- Coordinates are `[lon, lat]`, SRID 4326. Enforced by: nothing beyond Pydantic length checks (P4-04).
- Origin/destination never leave the local stack (D-004). Enforced by: nothing; currently violated (P2-01).
- Generated map data and the jar are never committed. Enforced by: `.gitignore` (by filename, per state).

## Boundaries

| Boundary | Comes in as | Checked by | Rule |
| --- | --- | --- | --- |
| Route request | JSON | Pydantic `RouteRequest` (length only) | parameterised SQL only |
| Bbox query | query floats | FastAPI type coercion | parameterised SQL; no size cap yet (P4-04) |
| OSM data | `.osm.pbf` over HTTPS | none | tags read, values never interpolated into SQL |
| GraphHopper reply | JSON | `raise_for_status`, key access | missing `paths` raises an unhandled 500 |

## Dependencies

| Dependency | Version | For | Why this one |
| --- | --- | --- | --- |
| PostGIS | `postgis/postgis:15-3.3` | camera storage, buffers, bbox queries | spatial SQL (D-001) |
| GraphHopper | 9.1 jar on `eclipse-temurin:17-jre` | road routing | per-request custom models (D-002) |
| FastAPI, uvicorn | ≥0.139, ≥0.51 | API | — |
| psycopg2-binary | ≥2.9.12 | DB client | — |
| requests | ≥2.34 | GraphHopper client | — |
| osmium | ≥4.3.1 | PBF parsing in ingester | — |
| Leaflet | 1.9.4 from unpkg | map UI | to be vendored (P2-02) |

## State and caches

| What | Where | Written by | Reset by | Committed? |
| --- | --- | --- | --- | --- |
| Camera data | `pgdata` Docker volume | `ingest_state.py` | `docker compose down -v` (destroys it) | no |
| Road graph | `graph-cache/` | GraphHopper on start | `ingest_state.sh` wipes it on state switch | no |
| Map extracts | `<state>-latest.osm.pbf` in repo root | `ingest_state.sh`, `setup-usa.sh` | by hand | no (gitignored per state) |
| GraphHopper jar | `graphhopper-web-9.1.jar` | by hand (P1-03) | by hand | no |

## Failure modes and observability

| Failure | User-visible behaviour | Detection | Recovery |
| --- | --- | --- | --- |
| PostGIS down / table missing | 500 "Spatial database failure." | API log | start `db`; create schema (P1-01) |
| GraphHopper still building | 502 | `docker logs -f alprevader-routing-1` | wait for import |
| Point outside loaded map | 400 out of bounds | API log | ingest that state |
| Heap too small | `routing` exits | container log | lower map size or raise `JAVA_OPTS` |

The API logs origin/destination at INFO; that should stop (P2-03). Security consequences live in
[SECURITY.md](SECURITY.md).

## Claims vs. code

- README: "your origin and destination never leave your machine". `index.html` sends typed addresses to
  nominatim.openstreetmap.org and loads tiles/Leaflet from third parties (P2-01, P2-02).
- README: "50-meter Capture Zone". Effective radius is ~100 m; decided radius is 75 m (D-009, P3-01).
- `cameras_evaded` counts cameras near the route corridor, not cameras avoided (P3-02).
- `build_custom_graphhopper_payload` docstring says ×0.0; code uses ×0.01 (P3-03).
- README Quick Start implies a fresh clone works; schema, `car.json` and the jar are missing (P1-01 to P1-03).
