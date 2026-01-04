import numpy as np
import pytest
from app.analysis.FractalDimension import fractal_dimension

def test_fractal_dimension_zeros():
    # A completely empty image (all zeros) should theoretically have 0 fractal dimension
    # or at least run without error.
    # Based on the code:
    # G_min = 0, G_max = 0, G = 1.
    # This might cause issues if not handled, let's see.
    # It requires a square image M x M.
    img = np.zeros((100, 100), dtype=np.uint8)
    
    # Simple check if it runs. The mathematical result for a plane is 2, 
    # but for "texture" fractal dimension it varies.
    # The code calculates D based on box counting of intensity surface.
    
    try:
        fd = fractal_dimension(img)
        assert isinstance(fd, float)
    except Exception as e:
        pytest.fail(f"fractal_dimension failed on zeros: {e}")

def test_fractal_dimension_random():
    np.random.seed(42)
    img = np.random.randint(0, 256, (100, 100), dtype=np.uint8)
    fd = fractal_dimension(img)
    assert isinstance(fd, float)
    # Fractal dimension of a surface should be between 2 and 3 usually, 
    # but this implementation might return something else (e.g. 1 to 2 for 1D profile??)
    # Usually for 2D images treated as 3D surfaces (x,y,intensity), D is between 2 and 3.
    # Let's just check it returns a finite number for now.
    assert np.isfinite(fd)

def test_fractal_dimension_gradient():
    # Smooth gradient
    x = np.linspace(0, 255, 100)
    y = np.linspace(0, 255, 100)
    xv, yv = np.meshgrid(x, y)
    img = (xv + yv) / 2
    img = img.astype(np.uint8)
    
    fd = fractal_dimension(img)
    assert np.isfinite(fd)
