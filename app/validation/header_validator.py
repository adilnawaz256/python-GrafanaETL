import logging
from typing import List, Dict, Tuple, Optional

logger = logging.getLogger("aramco_etl.validation.headers")

# Expected required columns per source type
EXPECTED_HEADERS: Dict[str, List[str]] = {
    "IMS": ['STIME', 'cscf'],
    "CMG": ['STime', 'cmg_1'],
    "CMM": ['STime', 'cmm'],
    "RAN": ['STime', 'd1_plmn', 'Cell Availability Raw  [%]'],
    "SMSC": ['STime', 'hostname_smsc'],
    "TRANSPORT": ['STime', 'n_interface'],
    "ALARMS": ['Alarm ID', 'Event Time'],
    "TICKETS": ['Issue key']
}

def detect_source_type(filename: str, headers: List[str]) -> str:
    """
    Detect domain source type from filename or headers.
    """
    fname_upper = filename.upper()
    if "TRANSPORT" in fname_upper:
        return "TRANSPORT"
    elif "IMS" in fname_upper:
        return "IMS"
    elif "CMG" in fname_upper:
        return "CMG"
    elif "CMM" in fname_upper:
        return "CMM"
    elif "RAN" in fname_upper:
        return "RAN"
    elif "SMSC" in fname_upper:
        return "SMSC"
    elif "ALARM" in fname_upper:
        return "ALARMS"
    elif "SD" in fname_upper or "TICKET" in fname_upper:
        return "TICKETS"

    # Fallback to header inspection
    h_set = set(headers)
    if "cscf" in h_set or "STIME" in h_set:
        return "IMS"
    elif "cmg_1" in h_set:
        return "CMG"
    elif "cmm" in h_set:
        return "CMM"
    elif "d1_plmn" in h_set:
        return "RAN"
    elif "hostname_smsc" in h_set:
        return "SMSC"
    elif "n_interface" in h_set:
        return "TRANSPORT"
    elif "Alarm ID" in h_set:
        return "ALARMS"
    elif "Issue key" in h_set:
        return "TICKETS"

    return "UNKNOWN"

def validate_headers(source_type: str, actual_headers: List[str]) -> Tuple[bool, Optional[str]]:
    """
    Validates if actual headers satisfy the required headers for the given source type.
    Returns (is_valid, error_message)
    """
    required = EXPECTED_HEADERS.get(source_type, [])
    actual_set = set(actual_headers)

    missing = [col for col in required if col not in actual_set]
    if missing:
        msg = f"Header mismatch for source {source_type}. Missing required columns: {', '.join(missing)}"
        logger.error(msg)
        return False, msg

    return True, None
