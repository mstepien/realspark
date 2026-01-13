from .extraction import extract_patches
from .classifiers import classify_global_medium, get_patch_embeddings
from .search import analyze_texture_consistency
from PIL import Image
import numpy as np

def analyze_art_medium(img: Image.Image):
    """
    Performs a multi-stage analysis to identify the artistic medium.
    1. Global CLIP classification.
    2. Local DINOv2 patch embedding and consistency check.
    """
    # 1. High-level classification
    global_result = classify_global_medium(img)
    
    # 2. Local texture analysis
    patches = extract_patches(img)
    # Since DINOv2 is heavy, we might want to limit the number of patches
    # if there are too many for a quick analysis.
    max_patches = 16
    if len(patches) > max_patches:
        # Sample patches (e.g. from the middle or spread out)
        indices = np.linspace(0, len(patches)-1, max_patches, dtype=int)
        patches = [patches[i] for i in indices]
        
    patch_embeddings = get_patch_embeddings(patches)
    consistency_score = analyze_texture_consistency(patch_embeddings)
    
    # Interpret consistency
    # High consistency (> 0.8) often means digital or flat color
    # Low consistency (< 0.5) often means complex traditional textures
    
    description = f"Likely {global_result['label']} (Confidence: {global_result['confidence']:.2f}). "
    if consistency_score > 0.8:
        description += "Texture is highly consistent, suggesting digital media or uniform washes."
    elif consistency_score < 0.5:
        description += "Texture is highly varied, suggesting complex physical brushwork or impasto."
    else:
        description += "Texture shows moderate variation consistent with standard artistic techniques."
        
    return {
        "medium": global_result["label"],
        "confidence": global_result["confidence"],
        "consistency_score": consistency_score,
        "description": description,
        "labels_weighted": global_result["all_scores"]
    }
