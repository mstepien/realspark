from skimage import exposure, color
from skimage.feature import hog
from skimage.transform import resize
from PIL import Image
import numpy as np
import io
import base64
from visualization import create_hog_visualization

def analyze_image(file_bytes: bytes):
    image = Image.open(io.BytesIO(file_bytes))
    # Convert to RGB to ensure 3 channels
    image = image.convert('RGB')
    np_image = np.array(image)
    
    width, height = image.size
    mean_color = np.mean(np_image, axis=(0, 1))
    
    # Compute HOG features
    # Resize to fixed size for consistent feature vector length
    resized_img = resize(np_image, (128, 64)) # Standard HOG size
    
    # Convert to grayscale as suggested by user
    gray_img = color.rgb2gray(resized_img)
    
    fd, hog_image = hog(gray_img, orientations=9, pixels_per_cell=(8, 8),
                    cells_per_block=(2, 2), visualize=True)

    # Generate visualization using the new module
    hog_image_b64 = create_hog_visualization(hog_image)

    return {
        "width": width,
        "height": height,
        "mean_color": mean_color.tolist(), # [r, g, b]
        "hog_features": fd.tolist(),
        "hog_image_b64": hog_image_b64
    }
