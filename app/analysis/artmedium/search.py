import numpy as np

def calculate_similarity(embeddings: np.ndarray):
    """
    Calculates the cosine similarity matrix for a set of embeddings.
    """
    # Normalize embeddings
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    norm_embeddings = embeddings / (norms + 1e-9)
    
    # Dot product gives cosine similarity
    similarity_matrix = np.dot(norm_embeddings, norm_embeddings.T)
    return similarity_matrix

def find_representative_clusters(embeddings: np.ndarray, threshold: float = 0.85):
    """
    Clusters patches based on similarity to find repeating textures.
    """
    if len(embeddings) < 2:
        return [0] # Just the first one
        
    sim_matrix = calculate_similarity(embeddings)
    
    # Simple threshold-based grouping
    clusters = []
    visited = set()
    
    for i in range(len(embeddings)):
        if i in visited:
            continue
            
        # Find all similar patches
        cluster = [j for j in range(len(embeddings)) if sim_matrix[i, j] > threshold]
        clusters.append(cluster)
        visited.update(cluster)
        
    return clusters

def analyze_texture_consistency(embeddings: np.ndarray):
    """
    Returns a score representing how consistent the texture is across the image.
    High consistency might indicate digital art or very uniform washes.
    Low consistency might indicate complex brushwork (Impasto).
    """
    if len(embeddings) < 2:
        return 1.0
        
    sim_matrix = calculate_similarity(embeddings)
    # Average off-diagonal similarity
    mask = ~np.eye(sim_matrix.shape[0], dtype=bool)
    avg_sim = np.mean(sim_matrix[mask])
    
    return float(avg_sim)
