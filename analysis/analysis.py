from skimage import color
from skimage.feature import hog
from skimage.transform import resize
from PIL import Image
import numpy as np
import io
***REMOVED***
import os

# Ensure we can import from the parent directory if needed, 
# but usually root is in path.
#Expose  analyze_image for backward compatibility with from analysis import analyze_image.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from visualization import create_hog_visualization

from .aiclassifiers import detect_ai

def prepare_image(file_bytes: bytes):
    """
    Opens image, converts to RGB, and extracts basic metadata.
    """
    image = Image.open(io.BytesIO(file_bytes))
    image = image.convert('RGB')
    np_image = np.array(image)
    width, height = image.size
    mean_color = np.mean(np_image, axis=(0, 1))
    return image, np_image, width, height, mean_color

def compute_hog(np_image):
    """
    Computes HOG features and visualization.
    """
    # Resize to a one standard size for better feature resolution (256x128)
    resized_img = resize(np_image, (256, 128)) 
    
    # Convert to grayscale
    gray_img = color.rgb2gray(resized_img)
    
    # Calculate HOG features
    fd, hog_image = hog(gray_img, orientations=9, pixels_per_cell=(8, 8),
                    cells_per_block=(2, 2), visualize=True)

    hog_image_buffer = create_hog_visualization(hog_image)
    return fd, hog_image_buffer

def analyze_image(file_bytes: bytes):
    """
    Wrapper for backward compatibility.
    """
    image, np_image, width, height, mean_color = prepare_image(file_bytes)
    fd, hog_image_buffer = compute_hog(np_image)
    ai_score = detect_ai(image)

    return {
        "width": width,
        "height": height,
        "mean_color": mean_color.tolist(), # [r, g, b]
        "hog_features": fd.tolist(),
        "hog_image_buffer": hog_image_buffer,
        "ai_probability": ai_score
    }

