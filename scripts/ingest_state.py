import osmium
import psycopg2
import sys
import os

class ALPRHandler(osmium.SimpleHandler):
    def __init__(self, db_conn):
        super(ALPRHandler, self).__init__()
        self.db_conn = db_conn
        self.cursor = self.db_conn.cursor()
        self.count = 0

    def node(self, n):
        if n.tags.get('man_made') == 'surveillance' and n.tags.get('surveillance:type') == 'ALPR':
            self.cursor.execute(
                "INSERT INTO alpr_cameras (node_id, location, capture_zone) VALUES (%s, ST_SetSRID(ST_MakePoint(%s, %s), 4326), ST_Transform(ST_Buffer(ST_Transform(ST_SetSRID(ST_MakePoint(%s, %s), 4326), 3857), 50), 4326)) ON CONFLICT (node_id) DO NOTHING",
                (n.id, n.location.lon, n.location.lat, n.location.lon, n.location.lat)
            )
            self.count += 1
            if self.count % 1000 == 0:
                self.db_conn.commit()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python ingest_state.py <file.osm.pbf>")
        sys.exit(1)

    filepath = sys.argv[1]
    db_name = os.environ.get('DB_NAME', 'alpr_evasion')
    db_user = os.environ.get('DB_USER', 'postgres')
    db_password = os.environ.get('DB_PASSWORD', 'password')
    db_host = os.environ.get('DB_HOST', 'db')
    db_port = os.environ.get('DB_PORT', '5432')

    print(f"[*] Connecting to PostGIS at {db_host}:{db_port}...")
    try:
        conn = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port
        )
    except Exception as e:
        print(f"Error connecting to database: {e}")
        sys.exit(1)

    print(f"[*] Scanning {filepath} for ALPR cameras...")
    handler = ALPRHandler(conn)
    handler.apply_file(filepath)
    conn.commit()
    print(f"[*] Ingestion complete! Added {handler.count} ALPR cameras to the database.")
