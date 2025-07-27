import os
import xlrd
from openpyxl import Workbook

def convert_xls_to_xlsx(xls_path, xlsx_path):
    book = xlrd.open_workbook(xls_path)
    sheet = book.sheet_by_index(0)

    wb = Workbook()
    ws = wb.active

    for row in range(sheet.nrows):
        for col in range(sheet.ncols):
            ws.cell(row=row+1, column=col+1).value = sheet.cell_value(row, col)

    wb.save(xlsx_path)

def convert_all_xls_in_folder(folder_path):
    xlsx_folder = os.path.join(folder_path, "xlsx")
    os.makedirs(xlsx_folder, exist_ok=True)

    for filename in os.listdir(folder_path):
        if filename.endswith(".xls") and not filename.startswith("~$"):  # exclude temp files
            xls_path = os.path.join(folder_path, filename)
            xlsx_path = os.path.join(xlsx_folder, filename.replace(".xls", ".xlsx"))
            try:
                convert_xls_to_xlsx(xls_path, xlsx_path)
                print(f"Converted: {filename} -> {os.path.basename(xlsx_path)}")
            except Exception as e:
                print(f"Failed to convert {filename}: {e}")

if __name__ == "__main__":
    target_folder = os.getcwd()  # or replace with your path e.g. 'r"C:\myfiles"'
    convert_all_xls_in_folder(target_folder)
