import os
import shutil
import pytest
from app.config.settings import settings
from app.discovery.file_discovery import FileInfo
from app.etl.pipeline import process_single_file

class MockCoreTable:
    def __init__(self):
        self.records = {} # (stime, d1_plmn) -> record dict

    def upsert_batch(self, records, conn=None):
        inserted = 0
        updated = 0
        for r in records:
            key = (r["stime"], r["d1_plmn"])
            if key in self.records:
                self.records[key] = r
                updated += 1
            else:
                self.records[key] = r
                inserted += 1
        return inserted + updated, 0

def test_failed_batch_does_not_block_next_batch_and_recovers_data(tmp_path, monkeypatch):
    # Setup temporary directory structure
    input_dir = tmp_path / "input"
    processing_dir = tmp_path / "processing"
    processed_dir = tmp_path / "processed"
    failed_dir = tmp_path / "failed"
    archive_dir = tmp_path / "archive"

    for d in (input_dir, processing_dir, processed_dir, failed_dir, archive_dir):
        d.mkdir()

    monkeypatch.setattr(settings, "INPUT_FOLDER", str(input_dir))
    monkeypatch.setattr(settings, "PROCESSING_FOLDER", str(processing_dir))
    monkeypatch.setattr(settings, "PROCESSED_FOLDER", str(processed_dir))
    monkeypatch.setattr(settings, "FAILED_FOLDER", str(failed_dir))
    monkeypatch.setattr(settings, "ARCHIVE_FOLDER", str(archive_dir))

    # Mock DB repositories & loader
    mock_db = MockCoreTable()

    # Patch repositories so DB queries return mock state
    monkeypatch.setattr("app.db.repositories.BatchRepository.find_batch_by_hash", lambda hash, conn=None: None)
    monkeypatch.setattr("app.db.repositories.BatchRepository.create_batch", lambda batch, conn=None: type('B', (), {'batch_id': 100})())
    monkeypatch.setattr("app.db.repositories.BatchRepository.update_batch_status", lambda **k: None)
    monkeypatch.setattr("app.db.repositories.ErrorRepository.record_error", lambda err, conn=None: None)
    monkeypatch.setattr("app.db.repositories.RawRecordRepository.save_raw_records", lambda recs, conn=None: None)
    monkeypatch.setattr("app.loaders.ran_loader.RANLoader.upsert_batch", mock_db.upsert_batch)

    # File 1: 14:00 (Valid RAN file)
    f1400 = input_dir / "RAN-2026-09-14T140000.csv"
    f1400.write_text(
        "STime,d1_plmn,Cell Availability Raw  [%]\n"
        "2026-09-14 13:45:00,Aramco,99.5\n"
        "2026-09-14 14:00:00,Aramco,99.6\n",
        encoding="utf-8"
    )

    # File 2: 14:15 (FAILED - Missing required "Cell Availability Raw  [%]" column)
    f1415 = input_dir / "RAN-2026-09-14T141500.csv"
    f1415.write_text(
        "STime,d1_plmn\n"
        "2026-09-14 14:15:00,Aramco\n",
        encoding="utf-8"
    )

    # File 3: 14:30 (Valid RAN file containing 14:15 data rolling backfill)
    f1430 = input_dir / "RAN-2026-09-14T143000.csv"
    f1430.write_text(
        "STime,d1_plmn,Cell Availability Raw  [%]\n"
        "2026-09-14 14:15:00,Aramco,99.7\n"  # 14:15 data included here!
        "2026-09-14 14:30:00,Aramco,99.8\n",
        encoding="utf-8"
    )

    # Process 14:00 file
    res1 = process_single_file(FileInfo(str(f1400)))
    assert res1 is True
    assert len(mock_db.records) == 2

    # Process 14:15 file -> FAILS
    res2 = process_single_file(FileInfo(str(f1415)))
    assert res2 is False # Returned False due to header mismatch
    # 14:15 file moved to failed directory
    assert (failed_dir / "RAN-2026-09-14T141500.csv").exists()

    # CRITICAL ASSERTION: Process 14:30 file -> MUST STILL RUN & SUCCEED!
    res3 = process_single_file(FileInfo(str(f1430)))
    assert res3 is True

    # VERIFICATION: The 14:15 timestamp record now exists EXACTLY ONCE in mock_db!
    from datetime import datetime
    target_dt = datetime(2026, 9, 14, 14, 15)
    timestamps_in_db = [k[0] for k in mock_db.records.keys()]
    assert timestamps_in_db.count(target_dt) == 1
    assert mock_db.records[(target_dt, "Aramco")]["cell_availability"] == 99.7
