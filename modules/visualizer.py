import matplotlib.pyplot as plt
import seaborn as sns

# 📊 Visualize Detected Table Regions
def visualize_table_detection(cell_indices, labels, image_path="table_detection.png"):
    plt.figure(figsize=(12, 8))
    sns.scatterplot(
        x=cell_indices[:, 1],  # column index
        y=-cell_indices[:, 0],  # negative row index to match spreadsheet layout
        hue=labels,
        palette="tab10",
        legend="full",
        s=40,
        alpha=0.8
    )
    plt.title("📐 Detected Table Regions in Excel Sheet")
    plt.xlabel("Column Index")
    plt.ylabel("Row Index")
    plt.grid(True)
    plt.legend(title="Table ID", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()

    # Save image
    plt.savefig(image_path)
    plt.close()