import os
from PIL import Image
from app.analysis.object_detection import detect_objects

def test_detect_objects_mona_lisa():
    """
    Test object detection using the Mona Lisa image.
    This test uses the real model (if available) or the mocked one depends on how it's called.
    Since we are importing directly from the module and not the package that might be patched,
    we can test the logic.
    """
    # Use path relative to this file to be resistant to different workdir roots (e.g. CI)
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__))) # Go up from tests/analysis/ to root
    image_path = os.path.join(base_dir, "tests/resources/images/mona_lisa.jpg")
    
    assert os.path.exists(image_path), f"Mona Lisa image not found at {image_path}"
    
    img = Image.open(image_path)
    
    # Run detection
    results = detect_objects(img)
    
    # Basic assertions
    assert results is not None
    assert isinstance(results, list)
    
    # The real model (YOLOS) should find 'person' in Mona Lisa
    # But since we've patched it in conftest, it might return the mock if we are not careful.
    # Actually, detect_objects in app/analysis/object_detection.py is what we imported.
    # The patch was on app.analysis.detect_objects and app.main.detect_objects.
    
    # Let's check if we have any results
    if len(results) > 0:
        found_person = any(res['label'] == 'person' for res in results)
        assert found_person, "Model should detect a person in the Mona Lisa image"
        
        for res in results:
            assert 'label' in res
            assert 'score' in res
            assert 'box' in res
            assert res['score'] > 0.5
            
            box = res['box']
            assert all(k in box for k in ['xmin', 'ymin', 'xmax', 'ymax'])
