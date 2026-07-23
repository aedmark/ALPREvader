#!/bin/bash
set -e

if [ -z "$1" ]; then
    echo "Usage: ./scripts/ingest_state.sh <state_name>"
    echo "Example: ./scripts/ingest_state.sh illinois"
    exit 1
fi

STATE=$1
FILE="${STATE}-latest.osm.pbf"
URL="https://download.geofabrik.de/north-america/us/${FILE}"

echo "=========================================="
echo " ALPR State Ingestion Pipeline"
echo " Target State: ${STATE}"
echo "=========================================="

echo "[*] Downloading ${FILE} from Geofabrik..."
wget "${URL}" -O "${FILE}" || { echo "Failed to download map data."; exit 1; }

echo "[*] Extracting ALPR Cameras into PostGIS (via Docker)..."
# We spin up the ingester container to run the python parsing script
docker compose run --rm ingester python3 scripts/ingest_state.py "${FILE}"

echo "=========================================="
echo "[*] Setup Complete for ${STATE} cameras!"
echo "=========================================="

read -p "Do you want to update the routing engine configuration to use ${STATE}'s map data now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo "[*] Updating config-alpr.yml to use ${FILE}..."
    # Use sed to replace datareader.file line
    sed -i -E "s/datareader.file: .*/datareader.file: ${FILE}/g" config-alpr.yml
    
    echo "[*] Wiping old graph-cache (using Docker to bypass root ownership)..."
    docker run --rm -v $(pwd):/app ubuntu rm -rf /app/graph-cache/*
    
    echo "[*] Restarting the routing engine container..."
    # If the stack is already up, restart routing. Otherwise, start it.
    docker compose up -d --force-recreate routing
    
    echo "[*] Routing engine is building the new ${STATE} graph cache in the background!"
    echo "    (You can monitor its progress with: docker logs -f alprevader-routing-1)"
else
    echo "[*] Skipping routing engine configuration."
    echo "    (Your evasive routing will still use the previously configured map data)."
fi
