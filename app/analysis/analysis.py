import cv2
from PIL import Image
import numpy as np
import io
import os
from PIL import ExifTags

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
    resized_img = cv2.resize(np_image, (256, 256), interpolation=cv2.INTER_AREA)

    # Use grayscale image for FD calculation
    if resized_img.ndim == 3:
        gray_img = cv2.cvtColor(resized_img, cv2.COLOR_RGB2GRAY)
    else:
        gray_img = resized_img
        
    # Ensure it is 0-255 uint8
    if gray_img.dtype != np.uint8:
        if gray_img.max() <= 1.0:
            gray_img = (gray_img * 255).astype(np.uint8)
        else:
            gray_img = gray_img.astype(np.uint8)
        
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

def extract_metadata(image: Image.Image):
    """
    Examines image metadata for clues of AI generation or suspicious lack of data.
    """
    tags = {}
    software = None
    is_suspicious = False
    descriptions = []
    
    # Check EXIF data
    exif = image.getexif()
    if exif:
        for tag_id, value in exif.items():
            tag = ExifTags.TAGS.get(tag_id, tag_id)
            tags[str(tag)] = str(value)
            if tag == 'Software':
                software = str(value)
    
    # Check info (often contains non-EXIF metadata like PNG text chunks)
    # Common AI software signatures:
    ai_keywords = ['Stable Diffusion', 'Midjourney', 'DALL-E', 'NovelAI', 'Automatic1111']
    
    # Check image.info keys and values (e.g., for PNG comments)
    for key, val in image.info.items():
        key_str = str(key)
        val_str = str(val)
        tags[f"info_{key_str}"] = val_str
        
        if isinstance(val, (str, bytes)):
            val_search = val if isinstance(val, str) else str(val)
            for kw in ai_keywords:
                if kw.lower() in val_search.lower() or kw.lower() in key_str.lower():
                    is_suspicious = True
                    descriptions.append(f"AI Keyword '{kw}' found in image info metadata.")
                    if not software and kw.lower() in val_search.lower():
                         software = kw
                    break
                    
    # Check Software tag for AI keywords
    if software:
        for kw in ai_keywords:
            if kw.lower() in software.lower():
                # Avoid duplicate descriptions
                ai_desc = f"AI Keyword '{kw}' found in Software tag."
                if ai_desc not in descriptions:
                    is_suspicious = True
                    descriptions.append(ai_desc)
                break

    # Summarize findings
    if is_suspicious:
        summary = "Suspicious: " + " ".join(descriptions)
    elif software:
        summary = f"Detected software: {software}"
    elif not tags:
        summary = "No metadata found."
    else:
        summary = f"Metadata found ({len(tags)} tags), no clear AI signatures detected."

    return {
        "tags": tags,
        "description": summary,
        "software": software,
        "is_suspicious": is_suspicious
    }

def analyze_image(file_bytes: bytes):
    """
    Wrapper for backward compatibility.
    """
    image, np_image, width, height, mean_color = prepare_image(file_bytes)
    ai_score = detect_ai(image)
    fractal_stats = compute_fractal_stats(np_image)
    metadata_analysis = extract_metadata(image)

    return {
        "width": width,
        "height": height,
        "mean_color": mean_color.tolist(), # [r, g, b]
        "ai_probability": ai_score,
        "metadata_analysis": metadata_analysis,
        **fractal_stats
    }

