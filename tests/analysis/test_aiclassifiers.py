from PIL import Image
from app.analysis.aiclassifiers import detect_ai

def test_detect_ai_unit():
    # Mocked to return 0.1 for 'AI' label in conftest
    img = Image.new('RGB', (100, 100), color='blue')
    score = detect_ai(img)
    assert score == 0.1
