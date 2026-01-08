from skimage import color
from skimage.feature import hog
from skimage.transform import resize
from PIL import Image
import numpy as np
import io
import os

from app.visualization import create_hog_visualization

from .aiclassifiers import detect_ai
from .fractaldim import fractal_dimension

def compute_fractal_stats(np_image):
    """
    Computes fractal dimensions for the image at different scales:
    - Default: Full range (2 to M//2)
    - (commented out) Small: Fine details (2 to M//8)
    - (commented out) Large: Coarse structure (M//8 to M//2)
    """
    # Resize to a smaller standard size for performance (Fractal Dim calculation is expensive)
    # Resizing to 256x256 ensures reasonable execution time while maintaining statistical validity.
    resized_img = resize(np_image, (256, 256), anti_aliasing=True)

    # Use grayscale image for FD calculation
    if resized_img.ndim == 3:
        gray_img = color.rgb2gray(resized_img)
        # Rescale to 0-255 uint8 as the algo expects standard image intensity range
        gray_img = (gray_img * 255).astype(np.uint8)
    else:
        # If already grayscale, ensure it is 0-255 uint8
        if resized_img.dtype != np.uint8:
             gray_img = (resized_img * 255).astype(np.uint8)
        else:
             gray_img = resized_img
        
    M = gray_img.shape[0]
    limit_small = max(3, M // 8)
    
    # Default (Full Range)
    fd_default = fractal_dimension(gray_img)
    
    # Small / Fine Details
    # fd_small = fractal_dimension(gray_img, min_box=2, max_box=limit_small)
    
    # Large / Coarse Structure
    # fd_large = fractal_dimension(gray_img, min_box=limit_small, max_box=M//2)
    
    return {
        "fd_default": fd_default,
        # "fd_small": fd_small,
        # "fd_large": fd_large
    }

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
    fractal_stats = compute_fractal_stats(np_image)

    return {
        "width": width,
        "height": height,
        "mean_color": mean_color.tolist(), # [r, g, b]
        "hog_features": fd.tolist(),
        "hog_image_buffer": hog_image_buffer,
        "ai_probability": ai_score,
        **fractal_stats
    }

