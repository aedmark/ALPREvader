#!/bin/bash
set -e

echo "=========================================="
echo " ALPR Evasion Router - USA Data Setup"
echo "=========================================="
echo "This script will download the USA OpenStreetMap data."
echo "WARNING: The USA map is ~9.5GB compressed and will require ~24GB of RAM to process."
echo ""

read -p "Do you want to proceed with downloading the USA map? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo "[*] Downloading us-latest.osm.pbf from Geofabrik..."
    # We use wget to resume if interrupted
    wget -c https://download.geofabrik.de/north-america/us-latest.osm.pbf -O us-latest.osm.pbf
    
    echo "[*] Download complete!"
    echo "Next steps:"
    echo "1. Run 'docker compose down'"
    echo "2. Wipe the old graph cache: 'rm -rf graph-cache/*'"
    echo "3. Run 'docker compose up -d' to start the ingestion."
    echo "4. Monitor logs with 'docker logs -f alprevader-routing-1' (this may take over an hour)."
else
    echo "Aborted."
fi
