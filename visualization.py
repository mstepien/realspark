import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64

def create_hog_visualization(hog_image):
    """
    Generates a visualization of HOG features using matplotlib.
    Returns a base64 encoded PNG string.
    """
    # Create a figure
    fig = plt.figure(figsize=(4, 4))
    
    # Display the HOG image in grayscale
    plt.imshow(hog_image, cmap='gray')
    plt.axis('off') # Hide axes
    plt.tight_layout()
    
    # Save to buffer
    buff = io.BytesIO()
    plt.savefig(buff, format="PNG", bbox_inches='tight', pad_inches=0)
    plt.close(fig) # Close the figure to free memory
    
    # Encode to base64
    return base64.b64encode(buff.getvalue()).decode("utf-8")
