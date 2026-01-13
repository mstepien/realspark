import torch
from transformers import pipeline, AutoProcessor, AutoModel
from PIL import Image
import numpy as np

# Cache for models and processors
_clip_pipeline = None
_dinov2_processor = None
_dinov2_model = None

MEDIUM_LABELS = {
    "Acrylic": ["Acrylic paint"],
    "Casein paint": ["Casein"],
    "Digital painting": ["Computer art", "Digital media"],
    "Encaustic": ["Hot wax painting"],
    "Fresco": ["Wall painting"],
    "Gouache": ["Opaque watercolor", "Body color"],
    "Ink": ["Sumi-e", "Ink wash painting"],
    "Oil": ["Oil paint"],
    "Pastels": ["Chalk pastels", "Oil pastels", "Hard pastels", "Soft pastels"],
    "Spray paint": ["Aerosol paint", "Canned paint"],
    "Tempera": ["Egg tempera", "Poster paint"],
    "Watercolor": ["Auraelle", "Transparent watercolor"]
}

def get_clip_pipeline():
    global _clip_pipeline
    if _clip_pipeline is None:
        # Using SigLIP or standard CLIP. Standard CLIP is more common for zero-shot.
        _clip_pipeline = pipeline("zero-shot-image-classification", model="openai/clip-vit-base-patch32")
    return _clip_pipeline

def get_dinov2():
    global _dinov2_processor, _dinov2_model
    if _dinov2_processor is None:
        _dinov2_processor = AutoProcessor.from_pretrained("facebook/dinov2-base")
        _dinov2_model = AutoModel.from_pretrained("facebook/dinov2-base")
    return _dinov2_processor, _dinov2_model

def classify_global_medium(img: Image.Image):
    """Uses CLIP for high-level medium classification."""
    clip = get_clip_pipeline()
    
    # Flatten the labels for CLIP
    candidate_labels = list(MEDIUM_LABELS.keys())
    
    results = clip(img, candidate_labels=candidate_labels)
    # Sort by score and get the top one
    top_result = results[0]
    return {
        "label": top_result["label"],
        "confidence": top_result["score"],
        "all_scores": {r["label"]: r["score"] for r in results}
    }

def get_patch_embeddings(patches: list):
    """Generates DINOv2 embeddings for a list of patches."""
    processor, model = get_dinov2()
    
    embeddings = []
    # Process in batches if necessary, but for now simple loop
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)
    
    with torch.no_grad():
        for patch in patches:
            inputs = processor(images=patch, return_tensors="pt").to(device)
            outputs = model(**inputs)
            # Use pooler_output or take the first token (CLS)
            # DINOv2 base has 768 dimensions
            embedding = outputs.pooler_output.cpu().numpy().flatten()
            embeddings.append(embedding)
            
    return np.array(embeddings)
