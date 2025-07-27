import json

def clean_json_data(json_file_path):
    """Cleans the JSON data by removing empty tables, redundant null columns, and entirely null rows."""
    with open(json_file_path, "r", encoding="utf-8") as file:
        data = json.load(file)
    
    tables = data.get("tables", {})
    cleaned_tables = {}
    
    for table_name, rows in tables.items():
        if not rows:  # Remove empty tables
            continue
        
        # Remove rows that are entirely null
        rows = [row for row in rows if any(v is not None for v in row.values())]
        if not rows:
            continue
        
        # Remove columns that are entirely null
        keys_to_remove = set(rows[0].keys())
        for row in rows:
            keys_to_remove.intersection_update({k for k, v in row.items() if v is None})
        
        for row in rows:
            for key in keys_to_remove:
                row.pop(key, None)
        
        cleaned_tables[table_name] = rows
    
    data["tables"] = cleaned_tables
    data["total_tables"] = len(cleaned_tables)
    
    with open(json_file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

    return len(cleaned_tables)