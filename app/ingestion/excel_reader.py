from typing import Dict, List, Tuple, Any
from pathlib import Path
import pandas as pd

def read_excel_file(file_path: str) -> Dict[str, Tuple[List[str], List[Dict[str, Any]]]]:
    """
    Reads an Excel file (.xlsx, .xls).
    Returns dict mapping sheet_name -> (headers_list, list_of_row_dicts).
    """
    path = Path(file_path)
    excel_file = pd.ExcelFile(path)
    result = {}

    for sheet_name in excel_file.sheet_names:
        df = pd.read_excel(excel_file, sheet_name=sheet_name)
        if df.empty:
            result[sheet_name] = ([], [])
            continue

        headers = [str(c).strip() for c in df.columns]
        rows = []
        for idx, row in df.iterrows():
            row_dict = {}
            for col, val in row.items():
                col_name = str(col).strip()
                if pd.isna(val):
                    row_dict[col_name] = None
                else:
                    row_dict[col_name] = val
            rows.append(row_dict)

        result[sheet_name] = (headers, rows)

    return result
