from transformers import pipeline
from PIL import Image
from threading import Lock

# Lazy loading of object detector
_object_detector = None
_lock = Lock()

def get_object_detector():
    global _object_detector
    with _lock:
        if _object_detector is None:
            # Use small and efficient YOLOS-Tiny for resource-constrained environments
            _object_detector = pipeline("object-detection", model="hustvl/yolos-tiny")
    return _object_detector

def warmup_object_detector():
    get_object_detector()

def detect_objects(image: Image.Image):
    """
    Detects objects in an image using YOLOS-Tiny.
    Returns a list of detections with labels, scores, and boxes.
    """
    try:
        detector = get_object_detector()
        results = detector(image)
        # Simplify results for the frontend/summary
        detections = []
        for res in results:
            if res['score'] > 0.5: # Threshold to filter low-confidence detections
                detections.append({
                    "label": res['label'],
                    "score": float(res['score']),
                    "box": res['box']
                })
        return detections
    except Exception as e:
        print(f"Object detection error: {e}")
        return None
