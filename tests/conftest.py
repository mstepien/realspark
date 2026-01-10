import sys
import os
# Removed: os.environ["TESTING"] = "true"

import pytest
import duckdb
import contextlib
from unittest.mock import MagicMock

# Add project root to path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from threading import Thread
import uvicorn
import httpx
import time
from app.main import app
import concurrent.futures
import asyncio

def run_async(coro):
    """
    Helper to run a coroutine in a separate thread/loop to avoid 
    'RuntimeError: asyncio.run() cannot be called from a running event loop'
    when combined with Playwright's sync fixtures.
    """
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(asyncio.run, coro)
        return future.result()

@pytest.fixture(scope="session", autouse=True)
def patch_app_settings():
    """
    Explicitly patch application settings for tests.
    """
    import app.main
    original_timeout = app.main.STEP_TIMEOUT
    app.main.STEP_TIMEOUT = 2
    yield
    app.main.STEP_TIMEOUT = original_timeout

@pytest.fixture(scope="session")
def mock_db_connection():
    """
    Creates an in-memory DuckDB connection for testing.
    Session scope ensures it's stable for the live_server thread.
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
            url VARCHAR,
            hog_features FLOAT[]
        )
    """)
    
    @contextlib.contextmanager
    def mock_get_conn():
        yield con

    # Manual patch
    import app.database
    original_get_conn = app.database.get_db_connection
    app.database.get_db_connection = mock_get_conn
    
    yield con
    
    app.database.get_db_connection = original_get_conn
    con.close()

@pytest.fixture(scope="function", autouse=True)
def db_session(mock_db_connection):
    """
    Cleans up the database before each test to ensure isolation.
    """
    mock_db_connection.execute("DELETE FROM image_stats")
    yield mock_db_connection

@pytest.fixture(scope="session")
def mock_storage_client():
    """
    Mocks the Google Cloud Storage client.
    """
    import app.storage
    mock_client = MagicMock()
    mock_bucket = MagicMock()
    mock_blob = MagicMock()
    
    mock_client.bucket.return_value = mock_bucket
    mock_bucket.blob.return_value = mock_blob
    mock_blob.public_url = "https://mock-storage.com/test-image.jpg"
    
    # Manual patch
    original_client = app.storage.storage_client
    app.storage.storage_client = mock_client
    
    yield mock_client
    
    app.storage.storage_client = original_client

@pytest.fixture(scope="session", autouse=True)
def mock_transformers():
    """
    Mocks the transformers pipeline to avoid downloading models during tests.
    """
    import app.analysis.aiclassifiers
    mock_pipeline = MagicMock()
    mock_pipeline.return_value = [
        {'label': 'AI', 'score': 0.1},
        {'label': 'Human', 'score': 0.9}
    ]
    
    def mock_get_pipeline(*args, **kwargs):
        return mock_pipeline
        
    original_pipeline = app.analysis.aiclassifiers.pipeline
    app.analysis.aiclassifiers.pipeline = mock_get_pipeline
    
    yield mock_pipeline
    
    app.analysis.aiclassifiers.pipeline = original_pipeline

class MockControl:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.delays = {}
        self.errors = {}
        self.return_values = {}

    def get_delay(self, name, default=1.5):
        return self.delays.get(name, default)

    def trigger_error(self, name):
        if name in self.errors:
            raise self.errors[name]

    def get_return(self, name, default):
        return self.return_values.get(name, default)

mock_control = MockControl()

@pytest.fixture(scope="session")
def control():
    return mock_control

@pytest.fixture(scope="session", autouse=True)
def mock_analysis_functions():
    """
    Mocks prepare_image, compute_hog, detect_ai, and compute_fractal_stats
    globally for the session to ensure live_server uses them.
    """
    import app.analysis
    import app.analysis.histogram
    import numpy as np
    from PIL import Image
    import io
    import time

    # Default mocks with a small delay to ensure polling catches the state
    def mock_prepare(content):
        mock_control.trigger_error("prepare")
        time.sleep(mock_control.get_delay("prepare"))
        img = Image.open(io.BytesIO(content))
        return img, np.zeros((100, 100, 3), dtype=np.uint8), 100, 100, np.array([128, 128, 128])

    def mock_hog(np_img):
        mock_control.trigger_error("hog")
        time.sleep(mock_control.get_delay("hog"))
        from PIL import Image
        import io
        img = Image.new('RGB', (100, 100), color='gray')
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        return mock_control.get_return("hog_fd", np.array([0.1] * 10)), buf

    def mock_detect_ai(img):
        mock_control.trigger_error("ai")
        time.sleep(mock_control.get_delay("ai"))
        return mock_control.get_return("ai_score", 0.15)

    def mock_fractal(np_img):
        mock_control.trigger_error("fractal")
        time.sleep(mock_control.get_delay("fractal"))
        return mock_control.get_return("fractal_stats", {"fd_default": 2.5, "fd_small": 2.1, "fd_large": 2.8})

    def mock_histogram(np_img):
        mock_control.trigger_error("histogram")
        time.sleep(mock_control.get_delay("histogram"))
        return {"histogram_r": [10]*256, "histogram_g": [20]*256, "histogram_b": [30]*256}

    import app.main
    import app.analysis
    import app.analysis.histogram
    
    originals = {
        'prepare_image': app.main.prepare_image,
        'compute_hog': app.main.compute_hog,
        'detect_ai': app.main.detect_ai,
        'compute_fractal_stats': app.main.compute_fractal_stats,
        'compute_histogram': app.main.compute_histogram
    }

    def with_logging(name, func):
        def wrapper(*args, **kwargs):
            print(f"MOCK CALL START: {name}")
            delay = mock_control.get_delay(name)
            print(f"MOCK CALL DELAY: {name} = {delay}")
            res = func(*args, **kwargs)
            print(f"MOCK CALL END: {name}")
            return res
        return wrapper

    # Patch modules
    app.main.prepare_image = app.analysis.prepare_image = with_logging("prepare", mock_prepare)
    app.main.compute_hog = app.analysis.compute_hog = with_logging("hog", mock_hog)
    app.main.detect_ai = app.analysis.detect_ai = with_logging("ai", mock_detect_ai)
    app.main.compute_fractal_stats = app.analysis.compute_fractal_stats = with_logging("fractal", mock_fractal)
    app.main.compute_histogram = app.analysis.histogram.compute_histogram = with_logging("histogram", mock_histogram)

    yield

    # Restore
    app.main.prepare_image = originals['prepare_image']
    app.main.compute_hog = originals['compute_hog']
    app.main.detect_ai = originals['detect_ai']
    app.main.compute_fractal_stats = originals['compute_fractal_stats']
    app.main.compute_histogram = originals['compute_histogram']

@pytest.fixture(scope="session")
def live_server():
    """
    Start the FastAPI application in a background thread for browser testing.
    Session scope ensures it stays alive for all browser tests.
    """
    def run_server():
        uvicorn.run(app, host="127.0.0.1", port=8765, log_level="error")
    
    thread = Thread(target=run_server, daemon=True)
    thread.start()
    
    # Wait for server to start
    max_retries = 30
    for _ in range(max_retries):
        try:
            with httpx.Client() as client:
                response = client.get("http://127.0.0.1:8765/")
                if response.status_code == 200:
                    break
        except Exception:
            pass
        time.sleep(0.5)
    else:
        pytest.fail("Live server failed to start within 15 seconds")
    
    yield "http://127.0.0.1:8765"

# Playwright configuration for frontend integration tests
def pytest_configure(config):
    """
    Configure pytest for Playwright browser tests.
    """
    config.addinivalue_line(
        "markers", "browser: mark test as a browser integration test"
    )

