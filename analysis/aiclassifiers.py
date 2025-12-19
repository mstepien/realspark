from transformers import pipeline
from PIL import Image

# Lazy loading of AI classifier
_ai_classifier = None

def get_ai_classifier():
    global _ai_classifier
    if _ai_classifier is None:
        # Use a high-quality AI image detector
        _ai_classifier = pipeline("image-classification", model="Ateeqq/ai-vs-human-image-detector")
    return _ai_classifier

def detect_ai(image: Image.Image):
    """
    Detects if an image is AI-generated.
    Returns the probability of being AI-generated (0.0 to 1.0).
    """
    try:
        classifier = get_ai_classifier()
        results = classifier(image)
        # Find the 'AI' label score
        for res in results:
            if res['label'].upper() == 'AI':
                return float(res['score'])
        return 0.0
    except Exception as e:
        print(f"AI detection error: {e}")
        return None
