from httpx import AsyncClient, ASGITransport
from app.main import app
from PIL import Image
import io
import numpy as np
import pytest
import asyncio
from tests.conftest import run_async

@pytest.fixture(autouse=True)
def fast_analysis(monkeypatch):
    """
    Mock heavy analysis functions to return instant results for faster testing.
    This overrides the global mock with delays from conftest.py.
    """
    def mock_prepare(content):
        img = Image.open(io.BytesIO(content))
        w, h = img.size
        return img, np.zeros((h, w, 3), dtype=np.uint8), w, h, np.array([0, 0, 0])

    def mock_hog(img):
        return np.zeros(10), io.BytesIO(b"fake_hog")

    def mock_ai(img):
        return 0.5

    def mock_fractal(img):
        return {"fd_default": 1.0}

    def mock_histogram(img):
        return {"histogram_r": [0]*256, "histogram_g": [0]*256, "histogram_b": [0]*256}

    monkeypatch.setattr("app.main.prepare_image", mock_prepare)
    monkeypatch.setattr("app.main.compute_hog", mock_hog)
    monkeypatch.setattr("app.main.detect_ai", mock_ai)
    monkeypatch.setattr("app.main.compute_fractal_stats", mock_fractal)
    monkeypatch.setattr("app.main.compute_histogram", mock_histogram)

def test_read_root():
    async def run():
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            response = await client.get("/")
            assert response.status_code == 200
            assert "Is that image created by AI?" in response.text
    run_async(run())

def test_get_stats_empty(mock_db_connection):
    async def run():
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            response = await client.get("/stats")
            assert response.status_code == 200
            data = response.json()
            assert data['total_images'] == 0
    run_async(run())

def test_upload_image_flow(mock_db_connection, mock_storage_client):
    async def run():
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            img = Image.new('RGB', (50, 50), color='blue')
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            img_bytes = img_byte_arr.getvalue()
            
            files = {
                'file': ('test.png', img_bytes, 'image/png')
            }
            
            response = await client.post("/upload", files=files)
            assert response.status_code == 200
            start_data = response.json()
            assert "task_id" in start_data
            task_id = start_data["task_id"]
            
            # Poll for completion
            max_retries = 100
            for _ in range(max_retries):
                res = await client.get(f"/progress/{task_id}")
                data = res.json()
                if data.get("status") == "Complete":
                    result = data["result"]
                    break
                if data.get("status") == "Error":
                    pytest.fail(f"Task failed: {data.get('error')}")
                await asyncio.sleep(0.01)
            else:
                pytest.fail("Task timed out")
            
            assert "id" in result
            assert result['stats']['width'] == 50
            assert result['stats']['height'] == 50
            assert "hog_image_url" in result['stats']
    run_async(run())

def test_upload_invalid_file():
    async def run():
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            files = {
                'file': ('test.txt', b'not an image', 'text/plain')
            }
            response = await client.post("/upload", files=files)
            assert response.status_code == 400
    run_async(run())

def test_partial_results_flow(mock_db_connection, mock_storage_client):
    async def run():
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            img = Image.new('RGB', (100, 100), color='red')
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            img_bytes = img_byte_arr.getvalue()
            
            files = {
                'file': ('partial_test.png', img_bytes, 'image/png')
            }
            
            response = await client.post("/upload", files=files)
            assert response.status_code == 200
            task_id = response.json()["task_id"]
            
            # Poll until we see partial results or completion
            seen_hog = False
            for _ in range(100):
                res = await client.get(f"/progress/{task_id}")
                data = res.json()
                if "partial_results" in data and data["partial_results"].get("hog_image_url"):
                    seen_hog = True
                if data.get("status") == "Complete":
                    break
                await asyncio.sleep(0.01)
                
            assert seen_hog, "Should have seen hog_image_url in partial results"
    run_async(run())

def test_task_abandonment_logic(mock_db_connection, mock_storage_client):
    async def run():
        transport = ASGITransport(app=app)
        # Use the same client to persist cookies (session_id)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            img = Image.new('RGB', (100, 100), color='green')
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            img_bytes = img_byte_arr.getvalue()
            
            # 1. Start first upload
            res1 = await client.post("/upload", files={'file': ('first.png', img_bytes, 'image/png')})
            assert res1.status_code == 200
            task_id1 = res1.json()["task_id"]
            
            # 2. Immediately start second upload
            res2 = await client.post("/upload", files={'file': ('second.png', img_bytes, 'image/png')})
            assert res2.status_code == 200
            task_id2 = res2.json()["task_id"]
            
            # 3. Verify first task is abandoned
            abandoned = False
            for _ in range(50):
                p1 = await client.get(f"/progress/{task_id1}")
                if p1.json().get("status") == "Abandoned":
                    abandoned = True
                    break
                await asyncio.sleep(0.01)
            assert abandoned, "First task should be Abandoned"
            
            # 4. Verify second task completes
            completed = False
            for _ in range(100):
                p2 = await client.get(f"/progress/{task_id2}")
                if p2.json().get("status") == "Complete":
                    completed = True
                    break
                await asyncio.sleep(0.01)
            assert completed, "Second task should complete"
            
            # 5. Verify only ONE record in DB (the second one)
            stats_res = await client.get("/stats")
            assert stats_res.json()["total_images"] == 1
    run_async(run())
