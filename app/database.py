import duckdb
import uuid
import os
import contextlib

@contextlib.contextmanager
def get_db_connection():
  db_path = os.environ.get("DATABASE_PATH", "image_stats.duckdb/image_stats.db")
  
  # Ensure directory exists
  db_dir = os.path.dirname(db_path)
  if db_dir and not os.path.exists(db_dir):
      os.makedirs(db_dir, exist_ok=True)
      
  con = duckdb.connect(db_path)
  try:
    yield con
  finally:
    con.close()

def init_db():
    with get_db_connection() as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS image_stats (
                id VARCHAR,
                filename VARCHAR,
                upload_time TIMESTAMP,
                width INTEGER,
                height INTEGER,
                mean_color_r DOUBLE,
                mean_color_g DOUBLE,
                mean_color_b DOUBLE,
                url VARCHAR,
                hog_features FLOAT[],
                metadata_analysis VARCHAR
            )
        """)

def save_stats(filename, url, stats):
    with get_db_connection() as con:
        image_id = str(uuid.uuid4())
        import json
        con.execute("""
            INSERT INTO image_stats (id, filename, upload_time, width, height, mean_color_r, mean_color_g, mean_color_b, url, hog_features, metadata_analysis)
            VALUES (?, ?, current_timestamp, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (image_id, filename, stats['width'], stats['height'], 
            stats['mean_color'][0], stats['mean_color'][1], stats['mean_color'][2], url, stats.get('hog_features'),
            json.dumps(stats.get('metadata_analysis'))))
        return image_id

def get_aggregate_stats():
    with get_db_connection() as con:
        # Example aggregate: count, avg width/height
        # We use try/except or check if table exists, but init_db should handle it.
        # If table is empty, result might be None or (0, None...).
        try:
            result = con.execute("""
                SELECT 
                    COUNT(*) as total_images,
                    AVG(width) as avg_width,
                    AVG(height) as avg_height,
                    AVG(mean_color_r) as avg_r,
                    AVG(mean_color_g) as avg_g,
                    AVG(mean_color_b) as avg_b
                FROM image_stats
            """).fetchone()
        except Exception:
            return {"total_images": 0}
    
    if not result or result[0] == 0:
        return {
            "total_images": 0,
            "avg_width": 0,
            "avg_height": 0,
            "avg_color": [0, 0, 0]
        }

    return {
        "total_images": result[0],
        "avg_width": round(result[1], 2) if result[1] else 0,
        "avg_height": round(result[2], 2) if result[2] else 0,
        "avg_color": [round(x, 2) if x else 0 for x in result[3:6]]
    }
