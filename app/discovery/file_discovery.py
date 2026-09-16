import os
import shutil
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.config.settings import settings
from app.utils.hashing import calculate_file_hash
from app.utils.timestamps import extract_timestamp_from_filename
from app.db.repositories import BatchRepository

logger = logging.getLogger("aramco_etl.discovery")

def ensure_directories():
    """Ensure all required pipeline directories exist."""
    for folder in [
        settings.INPUT_FOLDER,
        settings.PROCESSING_FOLDER,
        settings.PROCESSED_FOLDER,
        settings.FAILED_FOLDER,
        settings.ARCHIVE_FOLDER,
    ]:
        Path(folder).mkdir(parents=True, exist_ok=True)

class FileInfo:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.file_name = os.path.basename(file_path)
        self.file_extension = os.path.splitext(self.file_name)[1].lower()
        self.file_hash = calculate_file_hash(file_path)
        self.source_timestamp = extract_timestamp_from_filename(self.file_name)
        self.file_size = os.path.getsize(file_path)

def discover_new_files(check_db: bool = True) -> List[FileInfo]:
    """
    Scans configured input directory for supported Excel/CSV files.
    Calculates file hashes, extracts timestamps, filters already processed files,
    and sorts files by source timestamp chronologically.
    """
    ensure_directories()
    input_dir = Path(settings.INPUT_FOLDER)
    supported_exts = set(ext.strip().lower() for ext in settings.SUPPORTED_FILE_EXTENSIONS)

    files_found: List[FileInfo] = []

    for entry in input_dir.iterdir():
        if entry.is_file() and entry.suffix.lower() in supported_exts:
            try:
                info = FileInfo(str(entry))
                # Check DB for duplicate delivery
                if check_db:
                    existing = BatchRepository.find_batch_by_hash(info.file_hash)
                    if existing:
                        logger.info(f"Skipping already processed file '{info.file_name}' (Hash: {info.file_hash[:8]}...)")
                        # Move duplicate file to processed folder or archive
                        move_file(str(entry), settings.PROCESSED_FOLDER)
                        continue
                files_found.append(info)
            except Exception as e:
                logger.error(f"Error processing file metadata for {entry}: {e}")

    # Sort files chronologically by source_timestamp, falling back to filename
    files_found.sort(
        key=lambda f: (f.source_timestamp or datetime.min, f.file_name)
    )

    logger.info(f"Discovered {len(files_found)} new file(s) for processing.")
    return files_found

def move_file(source_path: str, target_dir: str) -> str:
    """
    Safely moves a file to target directory, handling filename collisions.
    """
    Path(target_dir).mkdir(parents=True, exist_ok=True)
    filename = os.path.basename(source_path)
    target_path = os.path.join(target_dir, filename)

    # If file exists in target, append timestamp to prevent overwrite
    if os.path.exists(target_path):
        base, ext = os.path.splitext(filename)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        target_path = os.path.join(target_dir, f"{base}_{timestamp}{ext}")

    shutil.move(source_path, target_path)
    logger.debug(f"Moved file {source_path} -> {target_path}")
    return target_path
