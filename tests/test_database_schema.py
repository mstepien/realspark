import pytest
import os
import duckdb
import app.database

def test_image_stats_schema_has_all_columns(tmp_path, monkeypatch):
    # Setup temporary database
    db_file = str(tmp_path / "test_schema.db")
    monkeypatch.setenv("DATABASE_PATH", db_file)
    
    app.database.init_db()
    
    with app.database.get_db_connection() as con:
        # Get column names
        res = con.execute("PRAGMA table_info('image_stats')").fetchall()
        columns = [row[1] for row in res]
        
        expected_columns = [
            'id', 'filename', 'upload_time', 'width', 'height',
            'mean_color_r', 'mean_color_g', 'mean_color_b', 'url',
            'hog_features', 'metadata_analysis'
        ]
        
        for col in expected_columns:
            assert col in columns, f"Missing column: {col}"

def test_save_and_retrieve_with_metadata(tmp_path, monkeypatch):
    # Setup temporary database
    db_file = str(tmp_path / "test_data.db")
    monkeypatch.setenv("DATABASE_PATH", db_file)
    
    app.database.init_db()
    
    test_stats = {
        'width': 100,
        'height': 100,
        'mean_color': [255, 0, 0],
        'hog_features': [0.1, 0.2],
        'metadata_analysis': {
            'software': 'TestSoft',
            'is_suspicious': False,
            'description': 'Test description',
            'tags': {'key': 'val'}
        }
    }
    
    image_id = app.database.save_stats("test.png", "http://example.com/test.png", test_stats)
    assert image_id is not None
    
    with app.database.get_db_connection() as con:
        row = con.execute("SELECT metadata_analysis FROM image_stats WHERE id = ?", (image_id,)).fetchone()
        assert row is not None
        import json
        metadata = json.loads(row[0])
        assert metadata['software'] == 'TestSoft'
        assert metadata['tags']['key'] == 'val'
