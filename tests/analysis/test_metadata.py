from PIL import Image, PngImagePlugin
import io
from app.analysis.analysis import extract_metadata

def test_extract_metadata_no_metadata():
    # Create an image without any metadata
    img = Image.new('RGB', (100, 100), color='white')
    result = extract_metadata(img)
    
    assert not result['is_suspicious']
    assert result['software'] is None
    assert "Metadata found" in result['description'] or "No metadata found" in result['description']

def test_extract_metadata_ai_software():
    # Create an image with AI software in EXIF
    img = Image.new('RGB', (100, 100))
    exif = img.getexif()
    # Software tag is 305
    exif[305] = "Stable Diffusion v1.5"
    
    # PIL doesn't allow direct saving of modified exif to the object in memory easily 
    # for all formats without re-opening. Let's simulate by saving and loading.
    buf = io.BytesIO()
    img.save(buf, format='JPEG', exif=exif)
    buf.seek(0)
    img_with_exif = Image.open(buf)
    
    result = extract_metadata(img_with_exif)
    assert result['is_suspicious']
    assert "Stable Diffusion" in result['software']
    assert "Suspicious" in result['description']

def test_extract_metadata_png_info():
    # Create a PNG with AI keywords in info
    img = Image.new('RGB', (100, 100))
    info = PngImagePlugin.PngInfo()
    info.add_text("parameters", "A beautiful painting, masterpiece, best quality, Stable Diffusion")
    
    buf = io.BytesIO()
    img.save(buf, format='PNG', pnginfo=info)
    buf.seek(0)
    img_with_info = Image.open(buf)
    
    result = extract_metadata(img_with_info)
    assert result['is_suspicious']
    assert "Stable Diffusion" in result['description']
    assert result['tags']['info_parameters'] == "A beautiful painting, masterpiece, best quality, Stable Diffusion"

def test_extract_metadata_multiple_tags():
    img = Image.new('RGB', (10, 10))
    img.info['comment'] = 'This is a test'
    img.info['author'] = 'Human'
    
    result = extract_metadata(img)
    assert not result['is_suspicious']
    assert result['tags']['info_comment'] == 'This is a test'
    assert result['tags']['info_author'] == 'Human'
    assert "Metadata found (2 tags)" in result['description']
