import json

def clean_json_data(json_file_path):
    """Cleans the JSON data by removing empty tables, redundant null columns, and entirely null rows."""
    with open(json_file_path, "r", encoding="utf-8") as file:
        data = json.load(file)
    
    tables = data.get("tables", {})
    cleaned_tables = {}
    
    for table_name, table_info in tables.items():
        # Extract the data rows (list of dictionaries)
        rows = table_info.get("data", [])
        headers = table_info.get("headers", [])
        
        if not rows:  # Remove empty tables
            continue
        
        # Remove rows that are entirely null
        cleaned_rows = [row for row in rows if any(v is not None for v in row.values())]
        if not cleaned_rows:
            continue
        
        # Remove columns that are entirely null across all rows
        if cleaned_rows:
            keys_to_remove = set(cleaned_rows[0].keys())
            for row in cleaned_rows:
                keys_to_remove.intersection_update({k for k, v in row.items() if v is None})
            
            for row in cleaned_rows:
                for key in keys_to_remove:
                    row.pop(key, None)
        
        # Preserve headers and cleaned data in the table
        cleaned_tables[table_name] = {
            "headers": headers,
            "data": cleaned_rows
        }
    
    data["tables"] = cleaned_tables
    data["total_tables"] = len(cleaned_tables)
    
    with open(json_file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

    return len(cleaned_tables)