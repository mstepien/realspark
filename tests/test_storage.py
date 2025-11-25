import pytest
import io
from storage import upload_to_gcs

@pytest.mark.asyncio
async def test_upload_to_gcs_mock(mock_storage_client):
    file_content = b"fake image data"
    file_obj = io.BytesIO(file_content)
    filename = "test.jpg"
    
    url = await upload_to_gcs(file_obj, filename)
    
    assert url == "https://mock-storage.com/test-image.jpg"
    
    # Verify client calls
    mock_storage_client.bucket.assert_called()
    mock_bucket = mock_storage_client.bucket.return_value
    mock_bucket.blob.assert_called_with(filename)
    mock_blob = mock_bucket.blob.return_value
    mock_blob.upload_from_file.assert_called()

@pytest.mark.asyncio
async def test_upload_no_client(monkeypatch):
    # Simulate no GCS client (local mode)
    monkeypatch.setattr("storage.storage_client", None)
    
    file_content = b"data"
    file_obj = io.BytesIO(file_content)
    
    url = await upload_to_gcs(file_obj, "local.jpg")
    
    assert "https://storage.googleapis.com/" in url
    assert "local.jpg" in url
