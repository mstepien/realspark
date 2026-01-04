import pytest
import numpy as np
from PIL import Image
import io
from app.analysis import analyze_image

def test_analyze_image_valid():
    # Create a simple 100x100 red image
    width, height = 100, 100
    red_image = Image.new('RGB', (width, height), color='red')
    
    # Save to bytes
    img_byte_arr = io.BytesIO()
    red_image.save(img_byte_arr, format='PNG')
    img_bytes = img_byte_arr.getvalue()
    
    # Analyze
    stats = analyze_image(img_bytes)
    
    assert stats['width'] == 100
    assert stats['height'] == 100
    # Red in RGB is (255, 0, 0)
    assert stats['mean_color'] == [255.0, 0.0, 0.0]
    
    # Check HOG
    assert "hog_features" in stats
    # HOG vector length depends on params. For 256x128, 8x8 cells, 2x2 blocks, 9 orientations:
    # Resizing set to (256, 128)
    # Blocks vertical: (256/8) - 1 = 31
    # Blocks horizontal: (128/8) - 1 = 15
    # Total blocks = 31 * 15 = 465
    # Features = 465 * 2 * 2 * 9 = 16740
    assert len(stats['hog_features']) == 16740
    
    # Check HOG visualization
    assert "hog_image_buffer" in stats
    assert isinstance(stats['hog_image_buffer'], io.BytesIO)
    assert len(stats['hog_image_buffer'].getvalue()) > 0
    
    # Check AI probability (mocked in conftest)
    assert "ai_probability" in stats
    assert isinstance(stats['ai_probability'], float)
    assert stats['ai_probability'] == 0.1

