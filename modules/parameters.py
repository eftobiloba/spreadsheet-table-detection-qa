import numpy as np
import matplotlib.pyplot as plt
from sklearn.neighbors import NearestNeighbors

def find_optimal_eps(cell_indices, k=4):
    """
    Uses k-distance method to determine the optimal eps for DBSCAN.
    :param cell_indices: Array of cell coordinates.
    :param k: The k-th nearest neighbor to consider.
    :return: Suggested eps value.
    """
    nbrs = NearestNeighbors(n_neighbors=k).fit(cell_indices)
    distances, indices = nbrs.kneighbors(cell_indices)
    
    # Sort the k-th nearest distances
    k_distances = np.sort(distances[:, k - 1])

    # Plot the k-distance graph
    plt.figure(figsize=(8, 5))
    plt.plot(k_distances)
    plt.xlabel("Points sorted by distance")
    plt.ylabel(f"{k}-th Nearest Neighbor Distance")
    plt.title("K-Distance Graph for DBSCAN")
    plt.grid(True)
    plt.show()

    # Suggest an eps value based on the elbow point
    elbow_index = np.argmax(np.diff(k_distances))  # Find steepest slope change
    suggested_eps = k_distances[elbow_index]
    print(f"Suggested eps: {suggested_eps:.2f}")

    return suggested_eps
