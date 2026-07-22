# **PROJECT REPORT: Sovereign Surveillance Evasion Routing (SSER) Architecture**

**OVERVIEW**

This document formalizes the architecture, data provenance, systemic mechanics, and ideological importance of the custom-built, local-metal Automatic License Plate Reader (ALPR, or FLOCK) evasion stack developed across our session. By decoupling navigation from surveillance-capitalist frameworks (such as Google Maps) and utilizing open-source geospatial tools, we establish a sovereign pipeline that respects user privacy and enforces semantic autonomy.

## **THE DATA: Where It Comes From**

We reject centralized, proprietary black-box APIs. Our surveillance threat landscape is crowdsourced and maintained transparently through the OpenStreetMap (OSM) ecosystem.

> * **The Source (DeFlock & OSM):** The foundational coordinates of surveillance cameras are mapped by decentralized privacy advocates using tools like *DeFlock*, which explicitly tags physical automated license plate readers within OpenStreetMap using the key-value pair surveillance:type=ALPR.

> 

> * **The Ingestion Pipeline:**

> 

  1. A declarative Python harvester script queries the public **Overpass API** mirrors using custom headers to bypass rate limits and transient gateway timeouts.  
  2. The script bounds our scope (e.g., the dense urban matrix of Chicago) and extracts raw node identifiers, geographic coordinates, and operators.  
  3. The data is ingested into a local **PostgreSQL** database utilizing the **PostGIS** spatial extension.  
  4. Using PostGIS spatial functions (ST\_Buffer), we draw an automated 50-meter perimeter (polygon) around each camera point, defining the **Capture Zone**—the physical field of view where an automated reader can log a vehicle's plate.


  


  

## **THE SYSTEM: How It Works**

The architecture operates as a multi-tier, sovereign state machine divided into four load-bearing layers:

> 1. **The Spatial Cache (PostgreSQL / PostGIS):** Serves as the static threat repository. It stores camera geometry as indexed spatial polygons (GEOMETRY(Polygon, 4326)), allowing sub-millisecond lookups for any given geographic corridor.

> 

> 2. **The Routing Engine (GraphHopper v9.1):** A high-performance Java-based mapping engine running entirely on local metal (localhost:8989). It compiles raw OSM .pbf terrain data (e.g., illinois-latest.osm.pbf) into an in-memory graph.  
   * *The Evasion Override:* By default, routing engines prioritize speed via pre-compiled Contraction Hierarchies (CH). To enforce dynamic avoidance, our stack disables CH ("ch.disable": True) on demand, forcing the engine to evaluate raw pathways.

   

> 3. **The Lexical Firewall (FastAPI Backend):** A lightweight, stateless Python orchestration layer (localhost:8000) acting as the mediator between the frontend UI and the routing engine.  
   * When a user requests a route, the API calculates a bounding box between origin and destination, queries PostGIS for intersecting Capture Zones, translates those polygons into valid GeoJSON Feature objects, and packages them into a GraphHopper custom\_model JSON payload.  
   * It instructs the engine to heavily penalize (multiplying road priority by 0.01) any edge intersecting a Capture Zone, forcing the router to find a path of least surveillance.

   

> 4. **The Frontend UI (Leaflet.js & Nominatim):** A zero-bloat browser interface. It translates human-readable addresses into coordinates via OpenStreetMap's native geocoder (**Nominatim**) and renders the resulting evasive GeoJSON vector geometry directly onto an open-source tile map.

> 

## 

## 

## 

## 

## **THE PHILOSOPHY: Sovereign Navigation**

> * **Breaking the Surveillance Loop:** Commercial mapping apps act as telemetry collection funnels, tracking and logging user movements in real-time. By hosting the map locally, no third-party entity learns where you start, where you travel, or what paths you chose to avoid.

> 

> * **Truth Over Convenience:** Corporate navigation prioritizes frictionless speed at the expense of civil liberties. Our stack acknowledges that avoiding mass surveillance introduces friction (longer distances, circuitous turns), treating that friction as a necessary tax for bodily and digital sovereignty.

> 

> * **Ephemeralization & Minimalist Craft:** We prove that complex geospatial orchestration does not require enterprise-grade cloud infrastructure or proprietary SDKs. By tying together vanilla JavaScript, Python, Java, and PostGIS, we achieve maximum functional output with minimal systemic bloat.
