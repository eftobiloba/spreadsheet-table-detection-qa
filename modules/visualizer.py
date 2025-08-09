import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def visualize_table_detection(cell_indices, labels, headers=None, comments=None, image_path="table_detection.png"):
    plt.figure(figsize=(12, 8))
    
    # Create custom legend labels for table clusters and noise
    unique_labels = sorted(set(labels) - {-1})  # Exclude noise (-1)
    hue_labels = {lbl: f"Table {lbl + 1}" for lbl in unique_labels}
    hue_labels[-1] = "Noise"  # Label for noise points
    
    # Map labels to custom legend names
    plot_labels = [hue_labels.get(lbl, "Noise") for lbl in labels]
    
    # Plot table clusters and noise points
    sns.scatterplot(
        x=cell_indices[:, 1],  # column index
        y=-cell_indices[:, 0],  # negative row index to match spreadsheet layout
        hue=plot_labels,
        palette="tab10",
        legend="full",
        s=40,
        alpha=0.8
    )
    
    # Plot headers (blue squares)
    if headers and len(headers) > 0:
        headers = np.array(headers)
        plt.scatter(
            x=headers[:, 1],
            y=-headers[:, 0],
            c="blue",
            marker="s",
            s=100,
            alpha=0.9,
            label="Headers"
        )
    
    # Plot comments (green triangles)
    if comments and len(comments) > 0:
        comments = np.array(comments)
        plt.scatter(
            x=comments[:, 1],
            y=-comments[:, 0],
            c="green",
            marker="^",
            s=100,
            alpha=0.9,
            label="Comments"
        )
    
    plt.title("📐 Detected Table Regions in Excel Sheet")
    plt.xlabel("Column Index")
    plt.ylabel("Row Index")
    plt.grid(True)
    plt.legend(title="Element Type", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()

    # Save image
    plt.savefig(image_path)
    plt.close()