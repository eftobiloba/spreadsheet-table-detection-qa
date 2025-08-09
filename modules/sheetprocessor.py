import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
import json
from modules.jsoncleaner import clean_json_data
from modules.parameters import find_optimal_eps
from modules.visualizer import visualize_table_detection

def detect_headers(table_df):
    """
    Detects header rows in a table DataFrame based on multiple features:
    - Text vs numeric ratio
    - Keyword presence
    - Uniqueness compared to following rows
    - Average text length

    Returns the index of the best header row (if any).
    """
    max_header_rows = min(5, len(table_df))
    header_keywords = {
        "name", "email", "phone", "tel", "date", "address", "role", "position",
        "amount", "status", "value", "id", "number", "category", "price", "qty"
    }

    scored_headers = []

    for i in range(max_header_rows):
        row = table_df.iloc[i]
        non_null_count = row.notna().sum()
        if non_null_count == 0:
            continue

        # Feature 1: Text score (non-numeric)
        text_count = sum(
            1 for val in row
            if pd.notna(val) and not str(val).replace(".", "", 1).isdigit()
        )
        text_score = text_count / non_null_count

        # Feature 2: Keyword score
        keyword_score = sum(
            1 for val in row
            if pd.notna(val) and any(kw in str(val).strip().lower() for kw in header_keywords)
        ) / non_null_count

        # Feature 3: Unique compared to next few rows
        compare_depth = min(3, len(table_df) - i - 1)
        all_next_values = set()
        for j in range(1, compare_depth + 1):
            all_next_values.update(
                str(val).strip().lower()
                for val in table_df.iloc[i + j]
                if pd.notna(val)
            )
        current_values = set(
            str(val).strip().lower() for val in row if pd.notna(val)
        )
        overlap = len(current_values.intersection(all_next_values)) / max(len(current_values), 1)
        unique_score = 1.0 - overlap

        # Feature 4: Length score (headers tend to be short)
        avg_length = np.mean([
            len(str(val)) for val in row if pd.notna(val)
        ])
        length_score = 1.0 if avg_length < 20 else 0.0

        # Combine all features
        header_score = (
            0.3 * text_score +
            0.25 * unique_score +
            0.25 * keyword_score +
            0.2 * length_score
        )

        # Debug print (optional)
        # print(f"Row {i}: text={text_score:.2f}, unique={unique_score:.2f}, keyword={keyword_score:.2f}, length={length_score:.2f}, total={header_score:.2f}")

        scored_headers.append((i, header_score))

    # Choose the best-scoring header if above threshold
    scored_headers.sort(key=lambda x: x[1], reverse=True)
    if scored_headers and scored_headers[0][1] > 0.6:
        return [scored_headers[0][0]]
    else:
        return []


def detect_comments(cell_indices, labels, df_original, table_bounds):
    """
    Detects comments from noise points and cells near tables.
    All noise points (label -1) are evaluated as potential comments using scoring.
    :param cell_indices: Array of non-empty cell coordinates.
    :param labels: DBSCAN cluster labels.
    :param df_original: Original DataFrame.
    :param table_bounds: List of (min_row, max_row, min_col, max_col) for each table.
    :return: List of comments with coordinates, values, and table associations.
    """
    comments = []
    proximity_distance = 2
    keywords = {"note", "comment", "description", "remark"}
    
    noise_indices = cell_indices[labels == -1]
    for i, j in noise_indices:
        value = df_original.iloc[i, j]
        if pd.isna(value):
            continue
        value = str(value).strip()
        
        length_score = min(1, len(value) / 50)
        word_count = len(value.split())
        complexity_score = min(1, word_count / 5)
        keyword_score = 1 if any(kw.lower() in value.lower() for kw in keywords) else 0
        comment_score = (length_score + complexity_score + keyword_score) / 3
        
        if comment_score > 0.6:
            comments.append({"row": int(i), "col": int(j), "value": value, "table_association": None})
    
    for table_idx, (min_row, max_row, min_col, max_col) in enumerate(table_bounds):
        row_range = range(max(0, min_row - proximity_distance), max_row + proximity_distance + 1)
        col_range = range(max(0, min_col - proximity_distance), max_col + proximity_distance + 1)
        
        for i in row_range:
            for j in col_range:
                if (min_row <= i <= max_row and min_col <= j <= max_col) or \
                   any(c["row"] == i and c["col"] == j for c in comments):
                    continue
                if i >= df_original.shape[0] or j >= df_original.shape[1]:
                    continue
                value = df_original.iloc[i, j]
                if pd.isna(value):
                    continue
                value = str(value).strip()
                
                length_score = min(1, len(value) / 50)
                word_count = len(value.split())
                complexity_score = min(1, word_count / 5)
                keyword_score = 1 if any(kw.lower() in value.lower() for kw in keywords) else 0
                comment_score = (length_score + complexity_score + keyword_score) / 3
                
                if comment_score > 0.6:
                    comments.append({
                        "row": int(i),
                        "col": int(j),
                        "value": value,
                        "table_association": f"table {table_idx + 1}"
                    })
    
    return comments

def detect_tables(file_path, visualize=False):
    df = pd.read_excel(file_path, header=None, dtype=str)
    df_original = df.copy()
    df = df.dropna(axis=1, how="all")

    data = df_original.replace("", np.nan).values
    cell_indices = np.argwhere(pd.notnull(data))
    
    tables = {}
    table_bounds = []

    if len(cell_indices) > 0:
        optimal_eps = find_optimal_eps(cell_indices)
        clustering = DBSCAN(eps=1.4, min_samples=2).fit(cell_indices)
        labels = clustering.labels_

        unique_labels = sorted(set(labels) - {-1})
        for i, label in enumerate(unique_labels, start=1):
            table_cells = cell_indices[labels == label]
            rows = table_cells[:, 0]
            cols = table_cells[:, 1]

            min_row, max_row = rows.min(), rows.max()
            min_col, max_col = cols.min(), cols.max()
            table_bounds.append((min_row, max_row, min_col, max_col))

            table_df = df_original.iloc[min_row:max_row + 1, min_col:max_col + 1].copy()
            table_df = table_df.applymap(lambda x: str(x).strip() if pd.notna(x) else "")

            header_indices = detect_headers(table_df)
            if header_indices:
                # Use first header row for column names
                header_row = table_df.iloc[header_indices[0]]
                table_df.columns = [str(val) if pd.notna(val) else f"col_{j}" for j, val in enumerate(header_row)]
                cols_series = pd.Series(table_df.columns)
                if cols_series.duplicated().any():
                    for dup in cols_series[cols_series.duplicated()].unique():
                        cols_series[cols_series == dup] = [f"{dup}_{j}" for j in range(sum(cols_series == dup))]
                    table_df.columns = cols_series
                # Exclude header rows from data
                data_df = table_df.iloc[len(header_indices):].reset_index(drop=True)
                # Store headers as dictionaries
                headers = [table_df.iloc[idx].to_dict() for idx in header_indices]
            else:
                table_df.columns = [f"col_{j}" for j in range(table_df.shape[1])]
                data_df = table_df
                headers = []

            data_df.replace(["", "nan", "None", "null"], None, inplace=True)
            tables[f"table {i}"] = {
                "data": data_df,
                "header_indices": header_indices,
                "headers": headers
            }

        comments = detect_comments(cell_indices, labels, df_original, table_bounds)

        table_jsons = {
            "total_tables": len(tables),
            "tables": {
                table_name: {
                    "headers": table_info["headers"],
                    "data": table_info["data"].to_dict(orient='records')
                }
                for table_name, table_info in tables.items()
            },
            "comments": comments
        }

        if visualize:
            header_cells = [
                (min_row + idx, col_idx)
                for table_name, table_info in tables.items()
                for idx in table_info["header_indices"]
                for col_idx in range(len(table_info["data"].columns))
            ]
            comment_cells = [(c["row"], c["col"]) for c in comments]
            visualize_table_detection(
                cell_indices,
                labels,
                headers=header_cells,
                comments=comment_cells,
                image_path="table_detection.png"
            )

        json_file_path = "tables.json"
        with open(json_file_path, "w", encoding="utf-8") as file:
            json.dump(table_jsons, file, indent=4)

        new_table_length = clean_json_data(json_file_path)

        return new_table_length, "table_detection.png" if visualize else None

    return 0, None