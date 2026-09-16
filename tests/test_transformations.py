import pytest
from app.transformation.ran_transformer import RANTransformer
from app.transformation.transport_transformer import TransportTransformer
from app.transformation.alarm_transformer import AlarmTransformer

def test_ran_transformer():
    row = {
        "STime": "2026-09-14 19:15:00",
        "d1_plmn": "Aramco",
        "Cell Availability Raw  [%]": "99.85",
        "E-RAB Drop Rate Raw  [%]": "0.12"
    }
    transformed = RANTransformer.transform_row(row, batch_id=101)
    assert transformed is not None
    assert transformed["d1_plmn"] == "Aramco"
    assert transformed["cell_availability"] == 99.85
    assert transformed["erab_drop_rate"] == 0.12
    assert transformed["source_batch_id"] == 101

def test_transport_device_extraction():
    device = TransportTransformer.extract_device_name_from_filename("transport_RYD-DCGW-01-2026-09-14T193556.csv")
    assert device == "RYD-DCGW-01"

    device2 = TransportTransformer.extract_device_name_from_filename("transport_DMM-DCGW1-2026-09-14T193454.csv")
    assert device2 == "DMM-DCGW1"

def test_alarm_transformer():
    row = {
        "Alarm ID": "1103837",
        "Event Time": "2026-09-14 19:39:59",
        "Original Severity": "Major",
        "Cleared": "False",
        "Alert Count": "5"
    }
    transformed = AlarmTransformer.transform_row(row, batch_id=202)
    assert transformed is not None
    assert transformed["alarm_id"] == "1103837"
    assert transformed["original_severity"] == "Major"
    assert transformed["cleared"] is False
    assert transformed["alert_count"] == 5
