import numpy as np
from PIL import Image, ImageDraw

def generate_fbm(shape, H):
    """
    Generates a Fractional Brownian Motion (fBM) surface approximation 
    using the spectral synthesis method.
    
    Args:
        shape (tuple): (height, width) of the output image. Should be square for best results.
        H (float): Hurst exponent (0 < H < 1). 
                   Theoretical Fractal Dimension D = 3 - H.
                   
    Returns:
        np.ndarray: 2D array of uint8 values (0-255).
    """
    M, N = shape
    # Create grid of frequencies
    # We want indices matching FFT frequency layout
    fx = np.fft.fftfreq(N)
    fy = np.fft.fftfreq(M)
    k_x, k_y = np.meshgrid(fx, fy)
    
    # Calculate magnitude of frequency vector k = sqrt(kx^2 + ky^2)
    # Avoid division by zero at DC component (0,0)
    k = np.sqrt(k_x**2 + k_y**2)
    k[0, 0] = 1.0  # arbitrary value to avoid inf, will set component to 0 later
    
    # Power Spectral Density P(f) ~ 1 / f^(beta)
    # beta = 2H + 2 (for 2D surface)
    beta = 2 * H + 2
    
    # Amplitude scales as sqrt(P(f)) ~ 1 / f^(beta/2) = 1 / f^(H+1)
    amplitude = k ** (-(beta - 1.0) / 2.0) # Actually usually beta=2H+2 for 2D, but let's stick to standard 1/f^alpha.
    # For fBM in 2D, spectral slope beta is related to H by beta = 2H + 2.
    # Phase is random
    phase = np.random.uniform(0, 2*np.pi, (M, N))
    
    # Random complex components
    # Real signal requires Hermitian symmetry in freq domain, but we can just take real part of IFFT
    # if we define full random phase.
    
    complex_spectrum = amplitude * np.exp(1j * phase)
    complex_spectrum[0, 0] = 0.0 # Zero mean
    
    # IFFT to get spatial domain
    img = np.fft.ifft2(complex_spectrum).real
    
    # Normalize to 0-255
    img = (img - img.min()) / (img.max() - img.min()) * 255
    return img.astype(np.uint8)

def generate_sierpinski_triangle(shape):
    """
    Generates a Sierpinski Triangle image.
    
    Args:
        shape (tuple): (height, width).
        
    Returns:
        np.ndarray: 2D array of uint8 values (0=background, 255=triangle).
    """
    height, width = shape
    img = Image.new('L', (width, height), 0)

    
    # Recursive function or Chaos game. Recursion is deterministic.
    def draw_triangle(x, y, size):
        if size < 2:
            return
        
        # Draw the triangle (inverted logic: we fill white, then remove center? 
        # Or Just draw points? Standard is fill, then remove middle inverted triangle)
        # Easier: Chaos game (random points) or simple recursion.
        # Let's do simple recursion filling top-1 (white).
        pass

    # Actually, chaos game is super easy for pixels
    # Vertices of the main triangle
    v1 = (width // 2, 10)
    v2 = (10, height - 10)
    v3 = (width - 10, height - 10)
    
    # Start point
    x, y = width // 2, height // 2
    
    pixels = img.load()
    import random
    
    # Chaos game
    # Warmup
    for _ in range(100):
        v = random.choice([v1, v2, v3])
        x, y = (x + v[0]) // 2, (y + v[1]) // 2
        
    for _ in range(50000): # Enough points to look like a triangle
        v = random.choice([v1, v2, v3])
        x, y = (x + v[0]) // 2, (y + v[1]) // 2
        if 0 <= x < width and 0 <= y < height:
             pixels[x, y] = 255
             
    return np.array(img)

def generate_koch_curve(shape, iterations=4):
    """
    Generates a Koch Curve (Snowflake edge) image.
    
    Args:
        shape (tuple): (height, width)
        iterations (int): number of recursive steps
        
    Returns:
        np.ndarray
    """
    height, width = shape
    img = Image.new('L', (width, height), 0)
    draw = ImageDraw.Draw(img)
    
    p1 = (10, height - height // 3)
    p2 = (width - 10, height - height // 3)
    
    def koch_line(start, end, depth):
        if depth == 0:
            draw.line([start, end], fill=255, width=1)
            return

        # Calculate points
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        
        p_a = (start[0] + dx/3, start[1] + dy/3)
        p_b = (start[0] + 2*dx/3, start[1] + 2*dy/3)
        
        # Tip of the triangle: rotate (p_b - p_a) by -60 degrees (or +60)
        # Vector p_a -> p_b is (dx/3, dy/3)
        vx = dx / 3
        vy = dy / 3
        
        # Rotate -60 deg (counter clockwise roughly standard)
        # x' = x cos - y sin
        # y' = x sin + y cos
        # angle = -pi/3
        angle = -np.pi / 3
        c = np.cos(angle)
        s = np.sin(angle)
        
        rx = vx * c - vy * s
        ry = vx * s + vy * c
        
        p_tip = (p_a[0] + rx, p_a[1] + ry)
        
        koch_line(start, p_a, depth-1)
        koch_line(p_a, p_tip, depth-1)
        koch_line(p_tip, p_b, depth-1)
        koch_line(p_b, end, depth-1)
        
    koch_line(p1, p2, iterations)
    return np.array(img)
