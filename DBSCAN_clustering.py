import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
import json
from datetime import datetime

def detect_table_regions(df):
    """Identify distinct table regions using density-based clustering"""
    # Get coordinates of all non-empty cells
    non_empty = df.notna()
    coords = np.argwhere(non_empty.values)
    
    if len(coords) == 0:
        return []
    
    # Scale coordinates for clustering
    scaler = StandardScaler()
    scaled_coords = scaler.fit_transform(coords)
    
    # Cluster using DBSCAN with adaptive parameters
    eps = 1.5  # Starting eps value
    min_samples = 5
    
    while True:
        clustering = DBSCAN(eps=eps, min_samples=min_samples).fit(scaled_coords)
        labels = clustering.labels_
        n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
        
        if n_clusters > 1 or eps <= 0.5:
            break
        eps -= 0.1  # Reduce eps if no clusters found
    
    # Group cells by cluster
    clusters = {}
    for (row, col), label in zip(coords, labels):
        if label not in clusters:
            clusters[label] = {'rows': set(), 'cols': set()}
        clusters[label]['rows'].add(row)
        clusters[label]['cols'].add(col)
    
    # Convert to table regions
    table_regions = []
    for label, region in clusters.items():
        if label == -1:  # Skip noise
            continue
        min_row, max_row = min(region['rows']), max(region['rows'])
        min_col, max_col = min(region['cols']), max(region['cols'])
        table_regions.append((min_row, max_row, min_col, max_col))
    
    return sorted(table_regions, key=lambda x: (x[0], x[2]))

def convert_to_serializable(obj):
    """Convert various types to JSON-serializable formats"""
    if pd.isna(obj) or obj is None:
        return None
    if isinstance(obj, (np.integer, np.int64)):
        return int(obj)
    if isinstance(obj, (np.float64, np.float32)):
        return float(obj)
    if isinstance(obj, (datetime, pd.Timestamp)):
        return obj.isoformat()
    if isinstance(obj, (list, tuple, np.ndarray)):
        return [convert_to_serializable(x) for x in obj]
    if isinstance(obj, dict):
        return {k: convert_to_serializable(v) for k, v in obj.items()}
    return str(obj) if not isinstance(obj, (str, int, float, bool)) else obj

def extract_tables(df, table_regions):
    """Extract tables from identified regions"""
    tables = []
    for i, (min_row, max_row, min_col, max_col) in enumerate(table_regions):
        table_df = df.iloc[min_row:max_row+1, min_col:max_col+1].copy()
        
        # Auto-detect headers
        first_row = table_df.iloc[0].dropna()
        if (len(first_row) > 0 and 
            all(isinstance(x, str) and x.strip().istitle() 
                for x in first_row if pd.notna(x))):
            table_df.columns = [str(col).strip() for col in table_df.iloc[0]]
            table_df = table_df[1:]
        
        # Process table data
        table_data = []
        for _, row in table_df.iterrows():
            cleaned_row = {}
            for col, value in row.items():
                cleaned_row[str(col)] = convert_to_serializable(value)
            table_data.append(cleaned_row)
        
        tables.append({
            "table_id": i,
            "bounds": {
                "rows": (int(min_row), int(max_row)),
                "cols": (int(min_col), int(max_col))
            },
            "data": table_data
        })
    return tables

def process_sheet_to_json(file_path):
    """Process an Excel sheet to JSON with automatic table detection"""
    try:
        # Read Excel with date parsing
        df = pd.read_excel(file_path, header=None, 
                          converters={i: str for i in range(100)})  # Convert all columns to string initially
        
        # Detect table regions
        table_regions = detect_table_regions(df)
        if not table_regions:
            return {"error": "No tables detected in sheet"}
        
        # Extract tables
        tables = extract_tables(df, table_regions)
        
        return {"tables": tables}
    
    except Exception as e:
        return {"error": f"Processing failed: {str(e)}"}

# Example usage
if __name__ == "__main__":
    file_path = "example.xlsx"
    result = process_sheet_to_json(file_path)
    print(json.dumps(result, indent=4, ensure_ascii=False))