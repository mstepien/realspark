import cv2

def compute_histogram(np_image):
    """
    Computes RGB color histogram using OpenCV.
    
    Args:
        np_image: numpy array of the image (RGB format)
        
    Returns:
        dict: Contains histogram_r, histogram_g, histogram_b as lists
    """
    # Ensure image is in correct format
    if np_image.ndim == 2:
        # Grayscale image - compute single histogram
        hist = cv2.calcHist([np_image], [0], None, [256], [0, 256])
        hist = hist.flatten().tolist()
        return {
            "histogram_r": hist,
            "histogram_g": hist,
            "histogram_b": hist
        }
    
    # RGB image - compute histogram for each channel
    # OpenCV uses BGR by default, but our images are RGB from PIL
    # So channel 0 = R, channel 1 = G, channel 2 = B
    hist_r = cv2.calcHist([np_image], [0], None, [256], [0, 256])
    hist_g = cv2.calcHist([np_image], [1], None, [256], [0, 256])
    hist_b = cv2.calcHist([np_image], [2], None, [256], [0, 256])
    
    # Convert to lists for JSON serialization
    return {
        "histogram_r": hist_r.flatten().tolist(),
        "histogram_g": hist_g.flatten().tolist(),
        "histogram_b": hist_b.flatten().tolist()
    }
