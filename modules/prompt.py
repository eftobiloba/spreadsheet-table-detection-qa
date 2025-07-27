import os
import json
import pandas as pd

def json_to_csv_tables():
    """
    Reads a JSON file with tables and saves each table as a cleaned CSV file.
    Returns a dictionary with table names and their CSV string content.
    Skips misleading header rows and numeric column keys.
    """
    with open("tables.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    csv_outputs = {}
    for table_name, records in data["tables"].items():
        # Convert list of dicts to DataFrame
        df = pd.DataFrame(records)

        # Drop rows where the first column contains 'Table' (assumed to be the title row)
        first_col = df.columns[0]
        df = df[~df[first_col].astype(str).str.contains("Table", na=False)]

        # Reset index after dropping rows
        df = df.reset_index(drop=True)

        # Try to infer headers: use the first valid row as the header
        if len(df) > 1:
            df.columns = df.iloc[0]
            df = df.drop(index=0).reset_index(drop=True)

        # Optional: rename unnamed columns if any
        df.columns = [f"Column {i+1}" if pd.isna(col) or col == '' else col for i, col in enumerate(df.columns)]

        csv_outputs[table_name] = df.to_csv(index=False)

    return csv_outputs

tables = json_to_csv_tables()

def generate_prompt(question):
    
    gemini_prompt = f"""
    You are a question-answering system for tabular data.
    Below are tables in CSV format:

    {tables}

    Answer the user's question based on these tables.
    Provide accurate calculations or lookups as needed.
    Format the response as plain text without any Markdown symbols (e.g., no *, **, _, #, or `).
    Use indentation or numbering for clarity, but avoid special characters for formatting.

    Question: {question}
    """

    return gemini_prompt