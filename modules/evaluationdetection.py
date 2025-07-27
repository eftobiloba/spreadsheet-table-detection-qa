import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
import os
import json
from modules.parameters import find_optimal_eps

def detect_tables_bbox(file_path, sheet_name=None):
    df = pd.read_excel(file_path, sheet_name=sheet_name, header=None, dtype=str)
    df_original = df.copy()
    df = df.dropna(axis=1, how="all")

    data = df_original.replace("", np.nan).values
    cell_indices = np.argwhere(pd.notnull(data))

    bboxes = []

    if len(cell_indices) > 0:
        optimal_eps = find_optimal_eps(cell_indices)
        clustering = DBSCAN(eps=optimal_eps, min_samples=2).fit(cell_indices)
        labels = clustering.labels_

        unique_labels = sorted(set(labels) - {-1})
        for i, label in enumerate(unique_labels, start=1):
            table_cells = cell_indices[labels == label]
            rows = table_cells[:, 0]
            cols = table_cells[:, 1]

            min_row, max_row = rows.min(), rows.max()
            min_col, max_col = cols.min(), cols.max()

            bbox = {
                "table_id": f"table_{i}",
                "bounding_box": {
                    "top_row": int(min_row),
                    "bottom_row": int(max_row),
                    "left_col": int(min_col),
                    "right_col": int(max_col)
                }
            }
            bboxes.append(bbox)

    return bboxes
