import pytest
import os
import duckdb
from unittest.mock import MagicMock
***REMOVED***

# Add project root to path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture
def mock_db_connection(monkeypatch):
    """
    Creates an in-memory DuckDB connection for testing.
    Patches database.get_db_connection to return this connection.
    """
    # Use in-memory DB
    con = duckdb.connect(":memory:")
    
    # Initialize schema
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
            url VARCHAR
        )
    """)
    
    # Patch the get_db_connection function in database.py
    # We need to patch it so that every time it's called, it returns our in-memory connection
    # However, DuckDB connections aren't thread-safe or easily shared if closed.
    # A better approach for the app code would be dependency injection, but for now:
    
    def mock_get_conn():
        # Return a cursor/connection that points to our in-memory DB
        # Note: duckdb.connect(":memory:") creates a NEW db each time.
        # We want to share the SAME in-memory db.
        return con.cursor() 

    monkeypatch.setattr("database.get_db_connection", mock_get_conn)
    
    yield con
    con.close()

@pytest.fixture
def mock_storage_client(monkeypatch):
    """
    Mocks the Google Cloud Storage client.
    """
    mock_client = MagicMock()
    mock_bucket = MagicMock()
    mock_blob = MagicMock()
    
    mock_client.bucket.return_value = mock_bucket
    mock_bucket.blob.return_value = mock_blob
    mock_blob.public_url = "https://mock-storage.com/test-image.jpg"
    
    # Patch the storage_client in storage.py
    monkeypatch.setattr("storage.storage_client", mock_client)
    
    return mock_client
