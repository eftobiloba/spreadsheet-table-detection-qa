import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
import json
from modules.jsoncleaner import clean_json_data
from modules.parameters import find_optimal_eps

def detect_tables(file_path, visualize=False):
    df = pd.read_excel(file_path, header=None, dtype=str)
    df_original = df.copy()
    df = df.dropna(axis=1, how="all")

    data = df_original.replace("", np.nan).values
    cell_indices = np.argwhere(pd.notnull(data))
    
    tables = {}

    if len(cell_indices) > 0:
        optimal_eps = find_optimal_eps(cell_indices)
        clustering = DBSCAN(eps=1.4, min_samples=2).fit(cell_indices)
        labels = clustering.labels_

        unique_labels = sorted(set(labels) - {-1})
        for i, label in enumerate(unique_labels, start=1):
            # Get the coordinates of cells with this label
            table_cells = cell_indices[labels == label]
            rows = table_cells[:, 0]
            cols = table_cells[:, 1]

            min_row, max_row = rows.min(), rows.max()
            min_col, max_col = cols.min(), cols.max()

            # Extract the sub-DataFrame
            # Extract the sub-DataFrame from the original (with blank columns preserved)
            table_df = df_original.iloc[min_row:max_row + 1, min_col:max_col + 1].copy()
            table_df = table_df.applymap(lambda x: str(x).strip() if pd.notna(x) else "")

            # Deduplicate columns
            cols_series = pd.Series(table_df.columns)
            if cols_series.duplicated().any():
                for dup in cols_series[cols_series.duplicated()].unique():
                    cols_series[cols_series == dup] = [f"{dup}_{j}" for j in range(sum(cols_series == dup))]
                table_df.columns = cols_series

            table_df.replace(["", "nan", "None", "null"], None, inplace=True)
            tables[f"table {i}"] = table_df

        table_jsons = {
            "total_tables": len(tables),
            "tables": {
                table_name: table_df.to_dict(orient='records')
                for table_name, table_df in tables.items()
            }
        }

        if visualize:
            from modules.visualizer import visualize_table_detection
            visualize_table_detection(cell_indices, labels, image_path="table_detection.png")

        json_file_path = "tables.json"
        with open(json_file_path, "w", encoding="utf-8") as json_file:
            json.dump(table_jsons, json_file, indent=4)

        new_table_length = clean_json_data(json_file_path)

        return new_table_length, "table_detection.png" if visualize else None

    return 0, None