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
                metadata_analysis VARCHAR,
                art_medium_analysis VARCHAR,
                summary VARCHAR,
                ai_probability DOUBLE,
                fd_default DOUBLE
            )
        """)

def save_stats(filename, url, stats):
    with get_db_connection() as con:
        image_id = str(uuid.uuid4())
        import json
        con.execute("""
            INSERT INTO image_stats (id, filename, upload_time, width, height, mean_color_r, mean_color_g, mean_color_b, url, metadata_analysis, art_medium_analysis, summary, ai_probability, fd_default)
            VALUES (?, ?, current_timestamp, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (image_id, filename, stats['width'], stats['height'], 
            stats['mean_color'][0], stats['mean_color'][1], stats['mean_color'][2], url,
            json.dumps(stats.get('metadata_analysis')),
            json.dumps(stats.get('art_medium_analysis')),
            stats.get('summary'),
            stats.get('ai_probability'),
            stats.get('fd_default')))
        return image_id

def get_aggregate_stats():
    with get_db_connection() as con:
        try:
            # Basic stats
            basic_stats = con.execute("""
                SELECT 
                    COUNT(*) as total_images,
                    AVG(width) as avg_width,
                    AVG(height) as avg_height,
                    AVG(mean_color_r) as avg_r,
                    AVG(mean_color_g) as avg_g,
                    AVG(mean_color_b) as avg_b
                FROM image_stats
            """).fetchone()
            
            if not basic_stats or basic_stats[0] == 0:
                return {"total_images": 0, "ai_metadata": [], "human_metadata": [], "art_mediums": [], "fractal_dist": []}

            # Helper to get top metadata
            def get_top_metadata(is_ai=True):
                condition = "ai_probability >= 0.5" if is_ai else "ai_probability < 0.5"
                rows = con.execute(f"SELECT metadata_analysis FROM image_stats WHERE {condition}").fetchall()
                
                import json
                from collections import Counter
                counter = Counter()
                for row in rows:
                    if row[0]:
                        try:
                            meta = json.loads(row[0])
                            tags = meta.get('tags', {})
                            if isinstance(tags, dict):
                                for k, v in tags.items():
                                    counter[f"{k}: {v}"] += 1
                        except Exception:
                            continue
                return [{"label": k, "count": v} for k, v in counter.most_common(10)]

            ai_metadata = get_top_metadata(is_ai=True)
            human_metadata = get_top_metadata(is_ai=False)

            # Art mediums
            art_rows = con.execute("SELECT art_medium_analysis FROM image_stats").fetchall()
            import json
            from collections import Counter
            art_counter = Counter()
            for row in art_rows:
                if row[0]:
                    try:
                        art = json.loads(row[0])
                        medium = art.get('medium')
                        if medium:
                            art_counter[medium] += 1
                    except Exception:
                        continue
            art_mediums = [{"label": k, "count": v} for k, v in art_counter.items()]

            # Fractal Distribution (Binned - more granular for density plot)
            # Fractal dimension typically ranges from 2.0 to 3.0
            fd_rows = con.execute("SELECT fd_default FROM image_stats WHERE fd_default IS NOT NULL").fetchall()
            fd_values = [row[0] for row in fd_rows]
            
            fractal_dist = []
            if fd_values:
                # Create 50 bins from 2.0 to 3.0
                num_bins = 50
                step = 1.0 / num_bins
                bins = [2.0 + i*step for i in range(num_bins + 1)]
                counts = [0] * num_bins
                for v in fd_values:
                    v_clipped = max(2.0, min(2.999, v))
                    bin_idx = int((v_clipped - 2.0) / step)
                    if 0 <= bin_idx < num_bins:
                        counts[bin_idx] += 1
                
                for i in range(num_bins):
                    label = f"{bins[i]:.2f}"
                    fractal_dist.append({"label": label, "count": counts[i]})

            return {
                "total_images": basic_stats[0],
                "avg_width": round(basic_stats[1], 2) if basic_stats[1] else 0,
                "avg_height": round(basic_stats[2], 2) if basic_stats[2] else 0,
                "avg_color": [round(x, 2) if x else 0 for x in basic_stats[3:6]],
                "ai_metadata": ai_metadata,
                "human_metadata": human_metadata,
                "art_mediums": art_mediums,
                "fractal_dist": fractal_dist
            }
        except Exception as e:
            print(f"Error in get_aggregate_stats: {e}")
            return {"total_images": 0, "ai_metadata": [], "human_metadata": [], "art_mediums": [], "fractal_dist": []}
