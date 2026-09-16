import logging
from typing import Dict, Any, Tuple, Optional
from app.utils.timestamps import parse_datetime

logger = logging.getLogger("aramco_etl.validation.rows")

def validate_row(source_type: str, row_dict: Dict[str, Any], row_num: int) -> Tuple[bool, Optional[str]]:
    """
    Validates a single raw row dictionary before transformation.
    Checks that essential natural key fields are present and non-empty.
    """
    if not row_dict:
        return False, f"Row {row_num} is empty."

    if source_type == "IMS":
        stime = row_dict.get("STIME") or row_dict.get("STime")
        cscf = row_dict.get("cscf")
        if not stime or not parse_datetime(stime):
            return False, f"Row {row_num}: Invalid or missing STIME: '{stime}'"
        if not cscf or not str(cscf).strip():
            return False, f"Row {row_num}: Missing cscf"

    elif source_type == "CMG":
        stime = row_dict.get("STime") or row_dict.get("STIME")
        cmg = row_dict.get("cmg_1") or row_dict.get("cmg")
        if not stime or not parse_datetime(stime):
            return False, f"Row {row_num}: Invalid or missing STime: '{stime}'"
        if not cmg or not str(cmg).strip():
            return False, f"Row {row_num}: Missing cmg"

    elif source_type == "CMM":
        stime = row_dict.get("STime") or row_dict.get("STIME")
        cmm = row_dict.get("cmm")
        if not stime or not parse_datetime(stime):
            return False, f"Row {row_num}: Invalid or missing STime: '{stime}'"
        if not cmm or not str(cmm).strip():
            return False, f"Row {row_num}: Missing cmm"

    elif source_type == "RAN":
        stime = row_dict.get("STime") or row_dict.get("STIME")
        d1_plmn = row_dict.get("d1_plmn")
        if not stime or not parse_datetime(stime):
            return False, f"Row {row_num}: Invalid or missing STime: '{stime}'"
        if not d1_plmn or not str(d1_plmn).strip():
            return False, f"Row {row_num}: Missing d1_plmn"

    elif source_type == "SMSC":
        stime = row_dict.get("STime") or row_dict.get("STIME")
        hostname = row_dict.get("hostname_smsc")
        if not stime or not parse_datetime(stime):
            return False, f"Row {row_num}: Invalid or missing STime: '{stime}'"
        if not hostname or not str(hostname).strip():
            return False, f"Row {row_num}: Missing hostname_smsc"

    elif source_type == "TRANSPORT":
        stime = row_dict.get("STime") or row_dict.get("STIME")
        n_interface = row_dict.get("n_interface")
        if not stime or not parse_datetime(stime):
            return False, f"Row {row_num}: Invalid or missing STime: '{stime}'"
        if not n_interface or not str(n_interface).strip():
            return False, f"Row {row_num}: Missing n_interface"

    elif source_type == "ALARMS":
        alarm_id = row_dict.get("Alarm ID")
        event_time = row_dict.get("Event Time")
        if not alarm_id or not str(alarm_id).strip():
            return False, f"Row {row_num}: Missing Alarm ID"
        if not event_time or not parse_datetime(event_time):
            return False, f"Row {row_num}: Invalid or missing Event Time: '{event_time}'"

    elif source_type == "TICKETS":
        issue_key = row_dict.get("Issue key")
        if not issue_key or not str(issue_key).strip():
            return False, f"Row {row_num}: Missing Issue key"

    return True, None
