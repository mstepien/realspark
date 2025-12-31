import numpy as np

def fractal_dimension(image: np.ndarray, min_box: int = 2, max_box: int = None) -> float:
    """
    Calculates the fractal dimension of an image represented by a 2D numpy array.

    The algorithm is a modified box-counting algorithm as described by Wen-Li Lee and Kai-Sheng Hsieh.

    Args:
        image: A 2D array containing a grayscale image. Format should be equivalent to cv2.imread(flags=0).
               The size of the image has no constraints, but it typically works best on square images.
               If the image is not square, the algorithm uses a sliding window or similar logic based on M (height).
               This implementation assumes M is the dimension to iterate over.
        min_box: Minimum box size (L) to use. Default is 2.
        max_box: Maximum box size (L) to use. Default is M // 2.

    Returns:
        float: The fractal dimension Df.
    """
    if image.ndim != 2:
        raise ValueError(f"Input image must be a 2D array, got shape {image.shape}")

    M = image.shape[0]  # image height
    
    g_min = float(image.min())
    g_max = float(image.max())
    G = g_max - g_min + 1  # number of gray levels
    
    prev_n_r = -1.0
    r_nr_points = []

    if max_box is None:
        max_box = (M // 2)

    # L ranges from min_box up to max_box (inclusive)
    for L in range(min_box, max_box + 1):
        # h: height of the box. 
        # "minimum box height is 1"
        # G // (M // L)  approximates scaling height with box size
        # Avoid division by zero if M//L is 0 (unlikely given loop range)
        scale = M // L
        if scale == 0:
            h = 1 # Fallback, though loop prevents this
        else:
            h = max(1.0, G / scale) 

        n_r = 0.0
        r = L / M
        
        for i in range(0, M, L):
            for j in range(0, M, L):
                # Calculate number of boxes needed to cover intensity range
                # (G + h - 1) // h is ceil(G/h)
                num_height_levels = int((G + h - 1) // h)
                boxes = [[] for _ in range(num_height_levels)]
                
                # Extract the block. 
                # Use standard slicing [row_start:row_end, col_start:col_end]
                sub_image = image[i : i + L, j : j + L]
                
                for row in sub_image:
                    for pixel in row:
                        height_idx = int((pixel - g_min) // h)
                        # Safety check index
                        if 0 <= height_idx < len(boxes):
                            boxes[height_idx].append(pixel)
                
                non_empty_boxes = [b for b in boxes if len(b) > 0]
                if not non_empty_boxes:
                    continue
                    
                for box in non_empty_boxes:
                    std = np.std(box)
                    n_box_r = 2 * (std // h) + 1
                    n_r += n_box_r

        if n_r != prev_n_r:
            r_nr_points.append((r, n_r))
            prev_n_r = n_r

    if not r_nr_points:
        return 0.0

    # Linear regression to find D
    # x = log(1/r) = -log(r)
    # y = log(Nr)
    
    x = np.array([-np.log(p[0]) for p in r_nr_points])
    y = np.array([np.log(p[1]) for p in r_nr_points])
    
    # Polyfit degree 1
    if len(x) < 2:
         return 0.0 # Not enough points for fit
         
    d_val = np.polyfit(x, y, 1)[0]
    return float(d_val)
