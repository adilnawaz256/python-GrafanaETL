import re
from datetime import datetime
from typing import Optional

def extract_timestamp_from_filename(filename: str) -> Optional[datetime]:
    """
    Extract source timestamp from filename using regex patterns.
    Examples:
      - RAN-2026-09-14T193840.csv -> 2026-09-14 19:38:40
      - RAN_2026-09-15_14-15.xlsx -> 2026-09-15 14:15:00
      - transport_RYD-DCGW-01-2026-09-14T193556.csv -> 2026-09-14 19:35:56
    """
    # Pattern 1: YYYY-MM-DDTHHMMSS (e.g. 2026-09-14T193840)
    match1 = re.search(r'(\d{4}-\d{2}-\d{2})T(\d{2})(\d{2})(\d{2})', filename)
    if match1:
        date_str = match1.group(1)
        hh, mm, ss = match1.group(2), match1.group(3), match1.group(4)
        try:
            return datetime.strptime(f"{date_str} {hh}:{mm}:{ss}", "%Y-%m-%d %H:%M:%S")
        except ValueError:
            pass

    # Pattern 2: YYYY-MM-DD_HH-MM (e.g. 2026-09-15_14-15)
    match2 = re.search(r'(\d{4}-\d{2}-\d{2})[_T](\d{2})-(\d{2})', filename)
    if match2:
        date_str = match2.group(1)
        hh, mm = match2.group(2), match2.group(3)
        try:
            return datetime.strptime(f"{date_str} {hh}:{mm}:00", "%Y-%m-%d %H:%M:%S")
        except ValueError:
            pass

    # Pattern 3: YYYYMMDD_HHMMSS
    match3 = re.search(r'(\d{4})(\d{2})(\d{2})[_T]?(\d{2})(\d{2})(\d{2})', filename)
    if match3:
        try:
            return datetime(
                int(match3.group(1)), int(match3.group(2)), int(match3.group(3)),
                int(match3.group(4)), int(match3.group(5)), int(match3.group(6))
            )
        except ValueError:
            pass

    return None

def parse_datetime(val) -> Optional[datetime]:
    """
    Robustly parse datetime value from row data.
    """
    if val is None:
        return None
    if isinstance(val, datetime):
        return val
    val_str = str(val).strip()
    if not val_str or val_str.lower() in ("nan", "none", "null", "nat"):
        return None

    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y/%m/%d %H:%M:%S",
        "%d-%m-%Y %H:%M:%S",
        "%d/%m/%Y %H:%M:%S",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(val_str, fmt)
        except ValueError:
            pass
    return None
