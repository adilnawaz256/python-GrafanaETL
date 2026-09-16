import json
import logging
from typing import Optional, List, Dict, Any
import psycopg2.extras
from app.db.models import FileBatch, FileError, PipelineRun, RawRecord
from app.db.connection import get_db_connection

logger = logging.getLogger("aramco_etl.repositories")

class BatchRepository:
    @staticmethod
    def create_batch(batch: FileBatch, conn=None) -> FileBatch:
        query = """
            INSERT INTO etl_file_batches (
                file_name, file_type, source_type, file_timestamp, received_at,
                status, file_hash, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING batch_id;
        """
        def _exec(c):
            with c.cursor() as cur:
                cur.execute(query, (
                    batch.file_name, batch.file_type, batch.source_type,
                    batch.file_timestamp, batch.received_at, batch.status,
                    batch.file_hash, batch.created_at
                ))
                batch.batch_id = cur.fetchone()[0]
                return batch

        if conn:
            return _exec(conn)
        with get_db_connection() as c:
            return _exec(c)

    @staticmethod
    def update_batch_status(
        batch_id: int, status: str, total_rows: int = 0, inserted_rows: int = 0,
        updated_rows: int = 0, failed_rows: int = 0, error_message: Optional[str] = None,
        started_at=None, completed_at=None, conn=None
    ):
        query = """
            UPDATE etl_file_batches
            SET status = %s,
                total_rows = %s,
                inserted_rows = %s,
                updated_rows = %s,
                failed_rows = %s,
                error_message = %s,
                processing_started_at = COALESCE(%s, processing_started_at),
                processing_completed_at = COALESCE(%s, processing_completed_at)
            WHERE batch_id = %s;
        """
        def _exec(c):
            with c.cursor() as cur:
                cur.execute(query, (
                    status, total_rows, inserted_rows, updated_rows, failed_rows,
                    error_message, started_at, completed_at, batch_id
                ))

        if conn:
            _exec(conn)
        else:
            with get_db_connection() as c:
                _exec(c)

    @staticmethod
    def find_batch_by_hash(file_hash: str, conn=None) -> Optional[Dict[str, Any]]:
        query = """
            SELECT batch_id, file_name, status, file_hash, file_timestamp
            FROM etl_file_batches
            WHERE file_hash = %s AND status = 'SUCCESS'
            ORDER BY batch_id DESC LIMIT 1;
        """
        def _exec(c):
            with c.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute(query, (file_hash,))
                row = cur.fetchone()
                return dict(row) if row else None

        if conn:
            return _exec(conn)
        with get_db_connection() as c:
            return _exec(c)

    @staticmethod
    def find_batch_by_id(batch_id: int, conn=None) -> Optional[Dict[str, Any]]:
        query = """
            SELECT batch_id, file_name, file_type, source_type, status, file_hash, file_timestamp
            FROM etl_file_batches
            WHERE batch_id = %s;
        """
        def _exec(c):
            with c.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute(query, (batch_id,))
                row = cur.fetchone()
                return dict(row) if row else None

        if conn:
            return _exec(conn)
        with get_db_connection() as c:
            return _exec(c)

    @staticmethod
    def find_batch_by_filename(filename: str, conn=None) -> Optional[Dict[str, Any]]:
        query = """
            SELECT batch_id, file_name, file_type, source_type, status, file_hash, file_timestamp
            FROM etl_file_batches
            WHERE file_name = %s
            ORDER BY batch_id DESC LIMIT 1;
        """
        def _exec(c):
            with c.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute(query, (filename,))
                row = cur.fetchone()
                return dict(row) if row else None

        if conn:
            return _exec(conn)
        with get_db_connection() as c:
            return _exec(c)

class ErrorRepository:
    @staticmethod
    def record_error(error: FileError, conn=None):
        query = """
            INSERT INTO etl_file_errors (
                batch_id, error_type, error_message, sheet_name,
                row_number, column_name, raw_value, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING error_id;
        """
        def _exec(c):
            with c.cursor() as cur:
                cur.execute(query, (
                    error.batch_id, error.error_type, error.error_message,
                    error.sheet_name, error.row_number, error.column_name,
                    error.raw_value, error.created_at
                ))
                error.error_id = cur.fetchone()[0]

        if conn:
            _exec(conn)
        else:
            with get_db_connection() as c:
                _exec(c)

class RawRecordRepository:
    @staticmethod
    def save_raw_records(records: List[RawRecord], conn=None):
        if not records:
            return
        query = """
            INSERT INTO raw_source_records (
                batch_id, source_type, source_file_name, row_number, raw_data, loaded_at
            ) VALUES %s;
        """
        args_list = [
            (r.batch_id, r.source_type, r.source_file_name, r.row_number, json.dumps(r.raw_data), r.loaded_at)
            for r in records
        ]
        def _exec(c):
            with c.cursor() as cur:
                psycopg2.extras.execute_values(cur, query, args_list)

        if conn:
            _exec(conn)
        else:
            with get_db_connection() as c:
                _exec(c)
