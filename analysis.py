from PIL import Image
import numpy as np
import io

def analyze_image(file_bytes: bytes):
    image = Image.open(io.BytesIO(file_bytes))
    # Convert to RGB to ensure 3 channels
    image = image.convert('RGB')
    np_image = np.array(image)
    
    width, height = image.size
    mean_color = np.mean(np_image, axis=(0, 1))
    
    return {
        "width": width,
        "height": height,
        "mean_color": mean_color.tolist() # [r, g, b]
    }
