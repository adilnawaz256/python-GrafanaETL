import pytest
from app.discovery.file_discovery import discover_new_files
from app.config.settings import settings

def test_duplicate_file_skipping(tmp_path, monkeypatch):
    input_dir = tmp_path / "input"
    processed_dir = tmp_path / "processed"
    input_dir.mkdir()
    processed_dir.mkdir()

    monkeypatch.setattr(settings, "INPUT_FOLDER", str(input_dir))
    monkeypatch.setattr(settings, "PROCESSED_FOLDER", str(processed_dir))

    f1 = input_dir / "IMS-2026-09-14T190000.csv"
    f1.write_text("STIME,cscf\n2026-09-14 19:00:00,CSC01\n", encoding="utf-8")

    # Mock DB find_batch_by_hash returning existing success batch
    monkeypatch.setattr("app.db.repositories.BatchRepository.find_batch_by_hash", lambda hash, conn=None: {"batch_id": 99, "status": "SUCCESS"})

    discovered = discover_new_files(check_db=True)
    # File should be detected as duplicate and skipped/moved
    assert len(discovered) == 0
    assert not f1.exists()
    assert (processed_dir / "IMS-2026-09-14T190000.csv").exists()
