import numpy as np
from PIL import Image
import io
from app.analysis import analyze_image

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