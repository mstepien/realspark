import pytest
from PIL import Image
from app.analysis.artmedium import analyze_art_medium
from app.analysis.artmedium.extraction import extract_patches
import torch

def test_extract_patches():
    # Create a small test image
    img = Image.new('RGB', (500, 500), color='red')
    patches = extract_patches(img, size=224, stride=112)
    # Expected: (500-224)//112 + 1 = 3 patches per dimension -> 9 total
    assert len(patches) == 9
    assert patches[0].size == (224, 224)

def test_extract_patches_small_image():
    img = Image.new('RGB', (100, 100), color='blue')
    patches = extract_patches(img, size=224)
    assert len(patches) == 1
    assert patches[0].size == (224, 224)

@pytest.mark.asyncio
async def test_analyze_art_medium_basic(monkeypatch):
    # Mocking for speed/no-net
    class MockOutput:
        def __init__(self):
            self.pooler_output = torch.zeros((1, 768))
        def to(self, device):
            return self

    def mock_clip(*args, **kwargs):
        return [{"label": "Oil", "score": 0.95}]

    def mock_get_clip():
        return mock_clip

    def mock_get_dinov2():
        mock_model = type('MockModel', (), {
            'to': lambda self, device: self,
            '__call__': lambda self, **kwargs: MockOutput()
        })()
        def mock_processor(images, return_tensors):
            return type('MockInputs', (), {
                'to': lambda self, device: {'pixel_values': torch.zeros((1, 3, 224, 224))}
            })()
        return mock_processor, mock_model

    monkeypatch.setattr("app.analysis.artmedium.classifiers.get_clip_pipeline", mock_get_clip)
    monkeypatch.setattr("app.analysis.artmedium.classifiers.get_dinov2", mock_get_dinov2)

    img = Image.new('RGB', (300, 300), color='green')
    result = analyze_art_medium(img)
    
    assert "medium" in result
    assert "confidence" in result
    assert "description" in result
    assert result["medium"] == "Oil"
    assert result["confidence"] == 0.95
