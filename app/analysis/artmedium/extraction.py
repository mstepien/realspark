import numpy as np
from PIL import Image

def extract_patches(img: Image.Image, size: int = 224, stride: int = 112):
    """
    Extracts overlapping patches from an image.
    
    Args:
        img: PIL Image object.
        size: Width and height of each patch.
        stride: Distance between the starts of adjacent patches.
        
    Returns:
        A list of PIL Image objects (patches).
    """
    w, h = img.size
    patches = []
    
    # Ensure image is large enough for at least one patch
    if w < size or h < size:
        # If too small, just resize slightly to fit one patch or return the whole image resized
        return [img.resize((size, size))]
    
    for y in range(0, h - size + 1, stride):
        for x in range(0, w - size + 1, stride):
            patch = img.crop((x, y, x + size, y + size))
            patches.append(patch)
            
    # If no patches were extracted (due to stride vs size logic), return at least one center crop
    if not patches:
        left = (w - size) // 2
        top = (h - size) // 2
        patches.append(img.crop((left, top, left + size, top + size)))
        
    return patches
