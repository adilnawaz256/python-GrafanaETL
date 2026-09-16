import os
import tempfile
import pytest
from app.utils.hashing import calculate_file_hash
from app.utils.timestamps import extract_timestamp_from_filename
from app.discovery.file_discovery import discover_new_files, FileInfo
from app.config.settings import settings

def test_extract_timestamp_from_filename():
    ts1 = extract_timestamp_from_filename("RAN-2026-09-14T193840.csv")
    assert ts1 is not None
    assert ts1.year == 2026 and ts1.month == 9 and ts1.day == 14 and ts1.hour == 19 and ts1.minute == 38

    ts2 = extract_timestamp_from_filename("RAN_2026-09-15_14-15.xlsx")
    assert ts2 is not None
    assert ts2.hour == 14 and ts2.minute == 15

    ts3 = extract_timestamp_from_filename("transport_RYD-DCGW-01-2026-09-14T193556.csv")
    assert ts3 is not None
    assert ts3.day == 14 and ts3.hour == 19

def test_file_hash_calculation(tmp_path):
    f = tmp_path / "test.csv"
    f.write_text("STime,d1_plmn\n2026-09-14 19:00:00,Aramco\n", encoding="utf-8")

    h1 = calculate_file_hash(str(f))
    assert len(h1) == 64

    # Hash should change when content changes
    f.write_text("STime,d1_plmn\n2026-09-14 19:00:00,Aramco_Updated\n", encoding="utf-8")
    h2 = calculate_file_hash(str(f))
    assert h1 != h2

def test_file_discovery_sorting(tmp_path, monkeypatch):
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    monkeypatch.setattr(settings, "INPUT_FOLDER", str(input_dir))

    # Create 3 files out of order
    f3 = input_dir / "RAN-2026-09-14T143000.csv"
    f1 = input_dir / "RAN-2026-09-14T140000.csv"
    f2 = input_dir / "RAN-2026-09-14T141500.csv"

    for f in (f3, f1, f2):
        f.write_text("STime,d1_plmn\n", encoding="utf-8")

    discovered = discover_new_files(check_db=False)
    assert len(discovered) == 3
    assert discovered[0].file_name == "RAN-2026-09-14T140000.csv"
    assert discovered[1].file_name == "RAN-2026-09-14T141500.csv"
    assert discovered[2].file_name == "RAN-2026-09-14T143000.csv"
