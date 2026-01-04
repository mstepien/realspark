import duckdb
import uuid
import os

DB_PATH = os.environ.get("DATABASE_PATH", "image_stats.duckdb")

def get_db_connection():
    con = duckdb.connect(DB_PATH)
    return con

def init_db():
    con = get_db_connection()
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
            hog_features FLOAT[]
        )
    """)
    con.close()

def save_stats(filename, url, stats):
    con = get_db_connection()
    image_id = str(uuid.uuid4())
    
    con.execute("""
        INSERT INTO image_stats (id, filename, upload_time, width, height, mean_color_r, mean_color_g, mean_color_b, url, hog_features)
        VALUES (?, ?, current_timestamp, ?, ?, ?, ?, ?, ?, ?)
    """, (image_id, filename, stats['width'], stats['height'], 
          stats['mean_color'][0], stats['mean_color'][1], stats['mean_color'][2], url, stats.get('hog_features')))
    con.close()
    return image_id

def get_aggregate_stats():
    con = get_db_connection()
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
    con.close()
    
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
