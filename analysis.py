from skimage import exposure, color
from skimage.feature import hog
from skimage.transform import resize
from PIL import Image
import numpy as np
import io
from visualization import create_hog_visualization

def analyze_image(file_bytes: bytes):
    image = Image.open(io.BytesIO(file_bytes))
    # Convert to RGB to ensure 3 channels
    image = image.convert('RGB')
    np_image = np.array(image)
    
    width, height = image.size
    mean_color = np.mean(np_image, axis=(0, 1))
    
    # Compute HOG features
    # Resize to a one standard size for better feature resolution (256x128)
    resized_img = resize(np_image, (256, 128)) 
    
    # Convert to grayscale as suggested by user
    gray_img = color.rgb2gray(resized_img)
    
    # Calculate HOG features:
    # pixels_per_cell: Size (in pixels) of a cell. (8, 8) means each cell is 8x8 pixels. 
    #   - Smaller values catch finer details but increase feature vector size.
    # cells_per_block: Number of cells in each block for normalization. (2, 2) is standard.
    #   - Normalization makes the descriptor robust to illumination changes.
    fd, hog_image = hog(gray_img, orientations=9, pixels_per_cell=(8, 8),
                    cells_per_block=(2, 2), visualize=True)

    hog_image_buffer = create_hog_visualization(hog_image)

    return {
        "width": width,
        "height": height,
        "mean_color": mean_color.tolist(), # [r, g, b]
        "hog_features": fd.tolist(),
        "hog_image_buffer": hog_image_buffer
    }
