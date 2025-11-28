import pytest
import numpy as np
from PIL import Image
import io
from analysis import analyze_image

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
    # HOG vector length depends on params. For 128x64, 8x8 cells, 2x2 blocks, 9 orientations:
    # Blocks vertical: (128/8) - 1 = 15
    # Blocks horizontal: (64/8) - 1 = 7
    # Total blocks = 15 * 7 = 105
    # Features = 105 * 2 * 2 * 9 = 3780
    assert len(stats['hog_features']) == 3780
    
    # Check HOG visualization
    assert "hog_image_b64" in stats
    assert isinstance(stats['hog_image_b64'], str)
    assert len(stats['hog_image_b64']) > 0

def test_analyze_image_gradient():
    # Create a 2x2 image
    # (0,0): Black (0,0,0)
    # (0,1): White (255,255,255)
    # (1,0): White (255,255,255)
    # (1,1): Black (0,0,0)
    # Mean should be 127.5
    
    data = np.zeros((2, 2, 3), dtype=np.uint8)
    data[0, 1] = [255, 255, 255]
    data[1, 0] = [255, 255, 255]
    
    image = Image.fromarray(data)
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_bytes = img_byte_arr.getvalue()
    
    stats = analyze_image(img_bytes)
    
    assert stats['width'] == 2
    assert stats['height'] == 2
    assert stats['mean_color'] == [127.5, 127.5, 127.5]
