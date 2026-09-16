import pytest
from app.validation.header_validator import detect_source_type, validate_headers

def test_detect_source_type():
    assert detect_source_type("RAN-2026-09-14T193840.csv", []) == "RAN"
    assert detect_source_type("IMS-2026-09-14T193927.csv", []) == "IMS"
    assert detect_source_type("PS_Core_CMG_sftp-2026-09-14T194000.csv", []) == "CMG"
    assert detect_source_type("PS_Core_CMM_sftp-2026-09-14T194000.csv", []) == "CMM"
    assert detect_source_type("all_alarms-2026-09-14T194000.csv", []) == "ALARMS"
    assert detect_source_type("SD-2026-09-14T194921.csv", []) == "TICKETS"
    assert detect_source_type("transport_RYD-DCGW-01-2026-09-14T193556.csv", []) == "TRANSPORT"

def test_validate_headers_valid():
    valid, err = validate_headers("RAN", ['STime', 'd1_plmn', 'Cell Availability Raw  [%]'])
    assert valid is True
    assert err is None

def test_validate_headers_missing_column():
    valid, err = validate_headers("RAN", ['STime', 'd1_plmn'])
    assert valid is False
    assert "Missing required columns: Cell Availability Raw  [%]" in err
