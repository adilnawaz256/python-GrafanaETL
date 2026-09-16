import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from app.db.models import FileBatch, FileError, RawRecord
from app.db.repositories import BatchRepository, ErrorRepository, RawRecordRepository

logger = logging.getLogger("aramco_etl.batch_manager")

class BatchManager:
    @staticmethod
    def initialize_batch(
        file_name: str, file_type: str, source_type: str, file_hash: str,
        file_timestamp: Optional[datetime] = None, conn=None
    ) -> FileBatch:
        batch = FileBatch(
            file_name=file_name,
            file_type=file_type,
            source_type=source_type,
            file_hash=file_hash,
            file_timestamp=file_timestamp,
            received_at=datetime.utcnow(),
            status="RECEIVED"
        )
        batch = BatchRepository.create_batch(batch, conn=conn)
        logger.info(f"Initialized batch #{batch.batch_id} for file '{file_name}' ({source_type})")
        return batch

    @staticmethod
    def start_processing(batch_id: int, conn=None):
        BatchRepository.update_batch_status(
            batch_id=batch_id,
            status="PROCESSING",
            started_at=datetime.utcnow(),
            conn=conn
        )
        logger.info(f"Batch #{batch_id} status updated to PROCESSING")

    @staticmethod
    def record_raw_data(batch_id: int, source_type: str, file_name: str, rows: List[Dict[str, Any]], conn=None):
        raw_records = [
            RawRecord(
                batch_id=batch_id,
                source_type=source_type,
                source_file_name=file_name,
                row_number=idx + 1,
                raw_data=row_data,
                loaded_at=datetime.utcnow()
            )
            for idx, row_data in enumerate(rows)
        ]
        RawRecordRepository.save_raw_records(raw_records, conn=conn)
        logger.debug(f"Saved {len(raw_records)} raw records for batch #{batch_id}")

    @staticmethod
    def record_error(
        batch_id: int, error_type: str, error_message: str, sheet_name: Optional[str] = None,
        row_number: Optional[int] = None, column_name: Optional[str] = None, raw_value: Optional[str] = None,
        conn=None
    ):
        err = FileError(
            batch_id=batch_id,
            error_type=error_type,
            error_message=error_message,
            sheet_name=sheet_name,
            row_number=row_number,
            column_name=column_name,
            raw_value=raw_value,
            created_at=datetime.utcnow()
        )
        ErrorRepository.record_error(err, conn=conn)
        logger.error(f"Batch #{batch_id} Error [{error_type}]: {error_message}")

    @staticmethod
    def finalize_batch(
        batch_id: int, status: str, total_rows: int, inserted_rows: int, updated_rows: int,
        failed_rows: int, error_message: Optional[str] = None, conn=None
    ):
        BatchRepository.update_batch_status(
            batch_id=batch_id,
            status=status,
            total_rows=total_rows,
            inserted_rows=inserted_rows,
            updated_rows=updated_rows,
            failed_rows=failed_rows,
            error_message=error_message,
            completed_at=datetime.utcnow(),
            conn=conn
        )
        logger.info(
            f"Finalized batch #{batch_id} with status {status}. Total: {total_rows}, "
            f"Inserted/Updated: {inserted_rows}, Failed: {failed_rows}"
        )
