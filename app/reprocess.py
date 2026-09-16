import argparse
import sys
import os
import logging
from pathlib import Path
from app.db.repositories import BatchRepository
from app.discovery.file_discovery import FileInfo, move_file
from app.etl.pipeline import process_single_file
from app.config.settings import settings

logger = logging.getLogger("aramco_etl.reprocess")

def reprocess_batch(batch_id: int):
    logger.info(f"Attempting to reprocess batch_id #{batch_id}...")
    batch_info = BatchRepository.find_batch_id(batch_id)
    if not batch_info:
        logger.error(f"Batch #{batch_id} not found in etl_file_batches.")
        return False

    filename = batch_info["file_name"]
    return reprocess_file_by_name(filename)

def reprocess_file_by_name(filename: str):
    logger.info(f"Looking for file '{filename}' in failed/processed/archive directories...")
    search_folders = [
        settings.FAILED_FOLDER,
        settings.PROCESSED_FOLDER,
        settings.ARCHIVE_FOLDER,
        settings.INPUT_FOLDER
    ]

    target_file = None
    for folder in search_folders:
        p = Path(folder) / filename
        if p.exists():
            target_file = str(p)
            break

    if not target_file:
        logger.error(f"File '{filename}' could not be located in any directory.")
        return False

    # Move file back to input folder and process without hash duplicate block
    input_path = move_file(target_file, settings.INPUT_FOLDER)
    file_info = FileInfo(input_path)

    logger.info(f"Reprocessing file '{filename}' from path '{input_path}'...")
    success = process_single_file(file_info)
    if success:
        logger.info(f"Reprocessing of '{filename}' completed successfully.")
    else:
        logger.error(f"Reprocessing of '{filename}' failed.")
    return success

def main():
    parser = argparse.ArgumentParser(description="Reprocess Aramco ETL files or batches.")
    parser.add_argument("--batch-id", type=int, help="Batch ID to reprocess")
    parser.add_argument("--file", type=str, help="Filename to reprocess")

    args = parser.parse_args()

    if not args.batch_id and not args.file:
        parser.print_help()
        sys.exit(1)

    if args.batch_id:
        reprocess_batch(args.batch_id)
    elif args.file:
        reprocess_file_by_name(args.file)

if __name__ == "__main__":
    main()
