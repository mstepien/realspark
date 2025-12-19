import pytest
from fastapi.testclient import TestClient
from main import app
from PIL import Image
import io

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "Is that image created by AI?" in response.text

def test_get_stats_empty(mock_db_connection):
    response = client.get("/stats")
    assert response.status_code == 200
    data = response.json()
    assert data['total_images'] == 0

def test_upload_image_flow(mock_db_connection, mock_storage_client):
    # Create a valid image
    img = Image.new('RGB', (50, 50), color='blue')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_bytes = img_byte_arr.getvalue()
    
    files = {
        'file': ('test.png', img_bytes, 'image/png')
    }
    
    response = client.post("/upload", files=files)
    
    assert response.status_code == 200
    start_data = response.json()
    assert "task_id" in start_data
    task_id = start_data["task_id"]
    
    # Poll for completion
    import time
    max_retries = 10
    for _ in range(max_retries):
        progress_response = client.get(f"/progress/{task_id}")
        assert progress_response.status_code == 200
        task_data = progress_response.json()
        
        if task_data.get("status") == "Complete":
            data = task_data["result"]
            break
        
        if task_data.get("status") == "Error":
            pytest.fail(f"Task failed: {task_data.get('error')}")
            
        time.sleep(0.1)
    else:
        pytest.fail("Task timed out")
    
    assert "id" in data
    assert data['stats']['width'] == 50
    assert data['stats']['height'] == 50
    assert data['stats']['mean_color'] == [0.0, 0.0, 255.0]
    assert "hog_features" in data['stats']
    assert "hog_image_url" in data['stats']
    assert data['stats']['hog_image_url'].startswith("/tmp/")
    
    # Verify stats updated
    stats_response = client.get("/stats")
    stats_data = stats_response.json()
    assert stats_data['total_images'] == 1
    assert stats_data['avg_color'] == [0.0, 0.0, 255.0]

def test_upload_invalid_file():
    files = {
        'file': ('test.txt', b'not an image', 'text/plain')
    }
    response = client.post("/upload", files=files)
    assert response.status_code == 400
