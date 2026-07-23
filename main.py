import os
import logging
import json
import requests
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import List, Tuple

# Configure strict, readable logging.
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# In production, these MUST be environment variables.
DB_CONFIG = {
    "dbname": os.getenv("DB_NAME", "alpr_evasion"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "password"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432")
}

GRAPHHOPPER_URL = os.getenv("GRAPHHOPPER_URL", "http://localhost:8989/route")

app = FastAPI(title="ALPR Evasion Routing API", version="1.0.0")

@app.get("/")
def read_root():
    """Serve the main frontend interface."""
    return FileResponse("index.html")

# Configure the Lexical Firewall to allow cross-origin browser requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, this would be locked down to your specific frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RouteRequest(BaseModel):
    # Coordinates are expected as [longitude, latitude] to match GeoJSON standards
    origin: List[float] = Field(..., min_length=2, max_length=2, description="[lon, lat]")
    destination: List[float] = Field(..., min_length=2, max_length=2, description="[lon, lat]")
    profile: str = Field(default="car", description="Routing profile (e.g., car, bike, foot)")


class RouteResponse(BaseModel):
    route_geometry: dict
    cameras_evaded: int
    distance_meters: float
    instructions: list = []


def fetch_intersecting_zones(origin: List[float], destination: List[float]) -> List[dict]:
    """
    Calculates a bounding box between origin and destination, pads it to account for
    circuitous routes, and extracts all ALPR Capture Zones intersecting that box.
    """
    # Simple bounding box calculation
    min_lon = min(origin[0], destination[0])
    max_lon = max(origin[0], destination[0])
    min_lat = min(origin[1], destination[1])
    max_lat = max(origin[1], destination[1])

    # Pad the bounding box by ~0.1 degrees (roughly 11km) to allow the routing
    # engine room to maneuver around large clusters of cameras.
    padding = 0.1
    bbox = (min_lon - padding, min_lat - padding, max_lon + padding, max_lat + padding)

    query = """
        SELECT node_id, ST_AsGeoJSON(ST_Buffer(capture_zone::geography, 50)::geometry) as geometry
        FROM alpr_cameras
        WHERE ST_Intersects(
            capture_zone,
            ST_MakeEnvelope(%s, %s, %s, %s, 4326)
        );
    """

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        # RealDictCursor allows us to access columns by name easily
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, bbox)
            results = cur.fetchall()
            return results
    except Exception as e:
        logging.error(f"PostGIS query failed: {e}")
        raise HTTPException(status_code=500, detail="Spatial database failure.")
    finally:
        if 'conn' in locals() and conn:
            conn.close()


def build_custom_graphhopper_payload(origin: List[float], destination: List[float], zones: List[dict],
                                     profile: str) -> dict:
    """
    Translates PostGIS polygons into GraphHopper's Custom Model JSON syntax.
    We instruct GraphHopper to multiply priority by 0.0 within these areas.
    """
    areas = {}
    priority_rules = []

    for zone in zones:
        area_id = f"custom_alpr_{zone['node_id']}"

        # Parse the GeoJSON string returned by PostGIS
        geometry = json.loads(zone['geometry'])

        areas[area_id] = {
            "type": "Feature",
            "geometry": {
                "type": geometry['type'],
                "coordinates": geometry['coordinates']
            },
            "properties": {}
        }

        # This rule applies a severe penalty. The engine will route miles out of the way
        # to avoid this area, but will pass through if it is the only physical option.
        priority_rules.append({
            "if": f"in_{area_id}",
            "multiply_by": 0.01
        })

    payload = {
        "points": [
            [origin[0], origin[1]],
            [destination[0], destination[1]]
        ],
        "profile": profile,
        "elevation": False,
        "instructions": True,
        "calc_points": True,
        "points_encoded": False,  # We want plain GeoJSON back for the frontend
        "ch.disable": True,  # Force engine off the pre-compiled graph
        "custom_model": {
            "areas": areas,
            "priority": priority_rules
        }
    }

    return payload


@app.post("/api/v1/routes/evasive", response_model=RouteResponse)
def get_evasive_route(req: RouteRequest):
    """
    The core evasion endpoint. Orchestrates the spatial query and the routing engine.
    """
    logging.info(f"Route requested: {req.origin} -> {req.destination}")

    # 1. Fetch the threat landscape from our sovereign database.
    zones = fetch_intersecting_zones(req.origin, req.destination)
    logging.info(f"Found {len(zones)} Capture Zones in the routing corridor.")

    # 2. Build the exact constraints for GraphHopper.
    payload = build_custom_graphhopper_payload(req.origin, req.destination, zones, req.profile)

    # 3. Request the path from our local GraphHopper instance.
    try:
        gh_response = requests.post(GRAPHHOPPER_URL, json=payload, timeout=10)
        gh_response.raise_for_status()

        gh_data = gh_response.json()
        path = gh_data['paths'][0]

        return RouteResponse(
            route_geometry=path['points'],
            cameras_evaded=len(zones),
            distance_meters=path['distance'],
            instructions=path.get('instructions', [])
        )

    except requests.exceptions.RequestException as e:
        logging.error(f"GraphHopper engine failed to calculate route: {e}")
        # If GraphHopper returns a 400, it usually means the custom model is too complex
        # or the route is physically impossible (e.g., origin is inside a capture zone).
        if hasattr(e, 'response') and e.response is not None:
            response_text = e.response.text
            logging.error(f"Engine response: {response_text}")
            if "out of bounds" in response_text:
                raise HTTPException(status_code=400, detail="One or more route points are outside the loaded map boundaries.")
        raise HTTPException(status_code=502, detail="Routing engine failed to find a viable evasive path.")


@app.get("/api/v1/cameras/bbox")
def get_cameras_in_bbox(min_lon: float, min_lat: float, max_lon: float, max_lat: float):
    """
    Returns all ALPR capture zones within a given bounding box.
    """
    query = """
        SELECT node_id, ST_AsGeoJSON(ST_Buffer(capture_zone::geography, 50)::geometry) as geometry
        FROM alpr_cameras
        WHERE ST_Intersects(
            capture_zone,
            ST_MakeEnvelope(%s, %s, %s, %s, 4326)
        );
    """
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, (min_lon, min_lat, max_lon, max_lat))
            results = cur.fetchall()
            
            features = []
            for row in results:
                features.append({
                    "type": "Feature",
                    "properties": {"node_id": row["node_id"]},
                    "geometry": json.loads(row["geometry"])
                })
            return {"type": "FeatureCollection", "features": features}
    except Exception as e:
        logging.error(f"Failed to fetch cameras: {e}")
        raise HTTPException(status_code=500, detail="Database error")
    finally:
        if 'conn' in locals() and conn:
            conn.close()


if __name__ == "__main__":
    import uvicorn

    logging.info("Starting ALPR Evasion API...")
    uvicorn.run(app, host="0.0.0.0", port=8000)