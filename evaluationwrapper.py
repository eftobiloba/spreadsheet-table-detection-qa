import os
import json
import pandas as pd
from tqdm import tqdm
from modules.evaluationdetection import detect_tables_bbox  # Assuming this is your detection function

# Load your CSV containing spreadsheet info
csv_path = "spreadsheet_inventory_20250605_161423.csv"  # Replace with your actual CSV file path
df = pd.read_csv(csv_path)

output_dir = "predictions"
os.makedirs(output_dir, exist_ok=True)

for _, row in tqdm(df.iterrows(), total=len(df)):
    spreadsheet = row["Spreadsheet Name"]
    path = row["Absolute File Path"]

    # Get only the first sheet
    sheet_names = row["Worksheet Names"].split(";")
    first_sheet = sheet_names[0].strip()

    try:
        # Run table detection only on the first sheet
        bboxes = detect_tables_bbox(path, first_sheet)
        output_json = {
            "spreadsheet": spreadsheet,
            "tables": bboxes
        }

        json_name = f"{spreadsheet}_pred.json"  # <- Spaces are now preserved
        with open(os.path.join(output_dir, json_name), "w") as f:
            json.dump(output_json, f, indent=4)

    except Exception as e:
        print(f"Error in {spreadsheet} / {first_sheet}: {e}")
