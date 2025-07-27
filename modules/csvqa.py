from langchain_community.llms import GPT4All
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import os
import pandas as pd
import json

class CSVPromptQA:
    def __init__(self, json_file_path, model_path: str):
        """
        :param csv_tables: Dictionary of {table_name: csv_content}
        :param model_path: Path to GPT4All model.
        """ 
        self.json_file_path = json_file_path
        self.model_path = model_path
        self.llm = GPT4All(model=self.model_path, n_threads=8, verbose=True)

        self.prompt_template = PromptTemplate(
            input_variables=["tables_csv", "question"],
            template=(
                "You are a question-answering system for tabular data.\n"
                "Below are tables in CSV format:\n\n"
                "{tables_csv}\n\n"
                "Answer the user's question based on these tables. "
                "Provide accurate calculations or lookups as needed.\n\n"
                "Question: {question}"
            )
        )

        self.chain = LLMChain(llm=self.llm, prompt=self.prompt_template)

    def json_to_csv_tables(self, output_dir="csv_tables"):
        """
        Reads a JSON file with tables and saves each table as a cleaned CSV file.
        Returns a dictionary with table names and their CSV string content.
        Skips misleading header rows and numeric column keys.
        """
        os.makedirs(output_dir, exist_ok=True)
        with open(self.json_file_path, "r", encoding="utf-8") as f:
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

            # Save and store as CSV string
            csv_path = os.path.join(output_dir, f"{table_name}.csv")
            df.to_csv(csv_path, index=False)
            csv_outputs[table_name] = df.to_csv(index=False)

        self.csv_tables = csv_outputs
        print(csv_outputs)

    def get_all_csv_tables(self) -> str:
        all_csv_data = "\n\n".join(f"{k}:\n{v}" for k, v in self.csv_tables.items())
        return all_csv_data

    def ask(self, question: str) -> str:
        all_csv_data = "\n\n".join(f"{k}:\n{v}" for k, v in self.csv_tables.items())
        return self.chain.run(tables_csv=all_csv_data, question=question)
