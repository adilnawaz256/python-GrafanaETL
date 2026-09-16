import csv
from typing import List, Dict, Any, Tuple
from pathlib import Path

def read_csv_file(file_path: str) -> Tuple[List[str], List[Dict[str, Any]]]:
    """
    Reads a CSV file safely, stripping UTF-8 BOM if present.
    Returns:
      (headers_list, list_of_row_dicts)
    """
    path = Path(file_path)
    with path.open("r", encoding="utf-8-sig", errors="replace") as f:
        reader = csv.reader(f)
        headers = next(reader, None)
        if not headers:
            return [], []
        
        # Clean headers
        headers = [h.strip() for h in headers]
        
        rows = []
        for row in reader:
            if not row or not any(row):
                continue
            # Zip headers with row values
            row_dict = {headers[i]: row[i].strip() if i < len(row) else "" for i in range(len(headers))}
            rows.append(row_dict)
            
    return headers, rows
