# ALPR Evader

<img width="1578" height="851" alt="image" src="https://github.com/user-attachments/assets/3b32ed95-c082-4bbb-8809-4e6c3a48e88f" />

**ALPR Evader** is a local, privacy-first routing engine designed to help you navigate your city while avoiding Automatic License Plate Readers (ALPRs) aka traffic cameras. 

Instead of relying on commercial navigation apps that track your every move and feed you through surveillance dragnets, ALPR Evader uses open-source map data to calculate routes that physically bypass known camera locations, keeping your travel history private.

---

## Prerequisites

To run this on your own machine, you only need two things:
1. **Docker** and **Docker Compose** installed on your system.
2. A machine with a decent amount of RAM. (By default, the routing engine is configured to use up to 24GB of RAM to support massive map data, but you can lower this by editing the `JAVA_OPTS` in `docker-compose.yml` if you are only routing within a single state).

---

## Quick Start Guide

We've built a fully automated pipeline that downloads the roads and camera locations for any US state, builds the routing graph, and spins up the web interface for you.

### Step 1: Ingest Your State
Open your terminal and run the automated ingestion script, passing in the name of the state you want to route in (e.g., `iowa`, `illinois`, `california`):

```bash
./scripts/ingest_state.sh iowa
```

**What this script does:**
1. Downloads the latest OpenStreetMap data for your chosen state.
2. Scans the map to extract the coordinates of every known ALPR camera (tagged by privacy advocates on tools like DeFlock).
3. Injects those cameras into a local spatial database.
4. Asks you if you want to switch your routing engine to this state. **Hit `y` for yes!**

### Step 2: Start the Application
Once the ingestion script finishes and restarts the routing engine, bring up the rest of the application (the web API):

```bash
docker compose up -d
```
*(If you make changes to the frontend UI, run `docker compose up -d --build api` to refresh the cache!)*

### Step 3: Access the Web UI
Open your favorite web browser and navigate to:
**http://localhost:8000**

You can now enter an Origin and Destination within your ingested state. The engine will automatically calculate a path that avoids the known ALPR cameras!

---

## How It Works

If you're curious about the mechanics, ALPR Evader operates entirely on your own hardware using a 4-tier stack:

1. **The Spatial Database (PostGIS):** Stores the exact GPS coordinates of every camera in your state. When it ingests a camera, it automatically draws a 50-meter circular "Capture Zone" around it.
2. **The Routing Engine (GraphHopper):** A high-performance Java engine that holds the entire road network in its memory. 
3. **The API (FastAPI):** When you ask for a route, the API draws a box between your start and end points, grabs all the cameras inside that box from the database, and feeds them to GraphHopper with strict instructions: *"Do whatever it takes to avoid driving through these 50-meter Capture Zones."*
4. **The Frontend (Leaflet.js):** A lightweight, dark-mode web interface that converts your typed addresses into coordinates and draws the final, secure route on the map in blue.

---

## Philosophy: Sovereign Navigation

Commercial mapping apps act as telemetry collection funnels, tracking and logging your movements in real-time. Corporate navigation prioritizes frictionless speed at the expense of civil liberties. 

By hosting the map locally, no third-party entity learns where you start, where you travel, or what paths you chose to avoid. Our stack acknowledges that avoiding mass surveillance introduces friction (longer distances, circuitous turns), treating that friction as a necessary tax for bodily and digital sovereignty.

### How is this Different from Flockhopper?

That's a great question! **FlockHopper** is actually built on the exact same underlying ethos and data sources (DeFlock and OpenStreetMap), but the architecture and threat models are very different.

Here is exactly how **ALPR Evader** differs from FlockHopper:

### 1. Zero-Trust & Completely Self-Hosted (Air-Gappable)

FlockHopper is a hosted mobile app and website. While they are very privacy-centric (no accounts, no trackers), you still have to send your GPS coordinates to their remote servers to calculate a route. **ALPR Evader** runs 100% on your local metal. Once you ingest a state, you can physically disconnect your computer from the internet and calculate routes offline. Your origin and destination never leave your machine.

### 2. Algorithmic Transparency

With FlockHopper, the routing algorithm is a black box—you ask for a route and it hands you an alternative. With ALPR Evader, you literally control the physics of the evasion. You wrote the PostGIS queries that draw the 50-meter Capture Zones, and you control the exact mathematical penalty (`multiply_by: 0.01`) in the GraphHopper custom model. If you want a 100-meter buffer, you can just change the code.

### 3. Infinite Scalability & Sovereignty

FlockHopper's coverage is dictated by what the developer decides to support on their servers. Because you are downloading the raw `.osm.pbf` files directly from Geofabrik and ingesting them into your own PostgreSQL database, you own the entire map. You can ingest any country on earth, and add your own private camera coordinates into the database that aren't public on OpenStreetMap.

**In short:** FlockHopper is an incredible, user-friendly consumer app for people who want an easy alternative to Google Maps.**ALPR Evader** is a sovereign, self-hosted infrastructure project for power users who refuse to trust anyone's servers but their own.

---

## Project Manual

For a searchable guide to behavior, operation, architecture, trade-offs, and known limitations, open the
[ALPR Evader 3x manual](docs/manual/index.html). It keeps each subject's **what**, **how**, and **why** together and
links its claims back to the project's code and canonical documentation.
