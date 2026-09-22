import os
import logging
from typing import List, Dict, Any
from app.config.settings import settings
from app.discovery.file_discovery import discover_new_files, move_file, FileInfo
from app.ingestion.csv_reader import read_csv_file
from app.ingestion.excel_reader import read_excel_file
from app.validation.header_validator import detect_source_type, validate_headers
from app.validation.row_validator import validate_row
from app.transformation.ran_transformer import RANTransformer
from app.transformation.ims_transformer import IMSTransformer
from app.transformation.cmg_transformer import CMGTransformer
from app.transformation.cmm_transformer import CMMTransformer
from app.transformation.alarm_transformer import AlarmTransformer
from app.transformation.smsc_transformer import SMSCTransformer
from app.transformation.transport_transformer import TransportTransformer
from app.transformation.ticket_transformer import TicketTransformer
from app.transformation.mcx_transformer import MCXTransformer
from app.loaders.ran_loader import RANLoader
from app.loaders.ims_loader import IMSLoader
from app.loaders.cmg_loader import CMGLoader
from app.loaders.cmm_loader import CMMLoader
from app.loaders.alarm_loader import AlarmLoader
from app.loaders.smsc_loader import SMSCLoader
from app.loaders.transport_loader import TransportLoader
from app.loaders.ticket_loader import TicketLoader
from app.loaders.mcx_loader import MCXLoader
from app.ingestion.sftp_downloader import download_files_from_sftp
from app.etl.batch_manager import BatchManager
from app.alerts.notifier import Notifier

logger = logging.getLogger("aramco_etl.pipeline")


TRANSFORMERS = {
    "RAN": RANTransformer,
    "IMS": IMSTransformer,
    "CMG": CMGTransformer,
    "CMM": CMMTransformer,
    "ALARMS": AlarmTransformer,
    "SMSC": SMSCTransformer,
    "TRANSPORT": TransportTransformer,
    "TICKETS": TicketTransformer,
    "MCX": MCXTransformer,
}

LOADERS = {
    "RAN": RANLoader,
    "IMS": IMSLoader,
    "CMG": CMGLoader,
    "CMM": CMMLoader,
    "ALARMS": AlarmLoader,
    "SMSC": SMSCLoader,
    "TRANSPORT": TransportLoader,
    "TICKETS": TicketLoader,
    "MCX": MCXLoader,
}

def process_single_file(file_info: FileInfo, conn=None) -> bool:
    """
    Processes a single Excel/CSV file within an isolated exception handler.
    Guarantees that failure on this file does not stop future file processing.
    """
    file_path = file_info.file_path
    filename = file_info.file_name
    logger.info(f"Starting processing for file '{filename}'...")

    # Step 1: Move file to processing directory
    processing_path = move_file(file_path, settings.PROCESSING_FOLDER)

    batch = None
    try:
        # Step 2: Read raw file data
        if file_info.file_extension == ".csv":
            headers, raw_rows = read_csv_file(processing_path)
            sheets_data = {"Sheet1": (headers, raw_rows)}
        else:
            sheets_data = read_excel_file(processing_path)

        # Detect source domain type
        all_headers = []
        for h, _ in sheets_data.values():
            all_headers.extend(h)
        source_type = detect_source_type(filename, all_headers)

        # Step 3: Initialize batch in etl_file_batches
        batch = BatchManager.initialize_batch(
            file_name=filename,
            file_type=file_info.file_extension,
            source_type=source_type,
            file_hash=file_info.file_hash,
            file_timestamp=file_info.source_timestamp,
            conn=conn
        )
        BatchManager.start_processing(batch.batch_id, conn=conn)

        # Flatten rows across sheets
        all_rows: List[Dict[str, Any]] = []
        for sheet_name, (headers, rows) in sheets_data.items():
            all_rows.extend(rows)

        total_rows = len(all_rows)

        # Step 4: Save raw data into raw_source_records
        BatchManager.record_raw_data(
            batch_id=batch.batch_id,
            source_type=source_type,
            file_name=filename,
            rows=all_rows,
            conn=conn
        )

        # Step 5: Validate required headers
        is_valid_header, header_error_msg = validate_headers(source_type, all_headers)
        if not is_valid_header:
            BatchManager.record_error(
                batch_id=batch.batch_id,
                error_type="HEADER_MISMATCH",
                error_message=header_error_msg,
                conn=conn
            )
            BatchManager.finalize_batch(
                batch_id=batch.batch_id,
                status="FAILED",
                total_rows=total_rows,
                inserted_rows=0,
                updated_rows=0,
                failed_rows=total_rows,
                error_message=header_error_msg,
                conn=conn
            )
            Notifier.send_alert(
                source_type=source_type,
                file_name=filename,
                batch_id=batch.batch_id,
                status="FAILED",
                reason=header_error_msg
            )
            move_file(processing_path, settings.FAILED_FOLDER)
            return False

        # Step 6: Validate & transform rows
        transformer_cls = TRANSFORMERS.get(source_type)
        loader_cls = LOADERS.get(source_type)

        if not transformer_cls or not loader_cls:
            err_msg = f"No transformer/loader registered for source type '{source_type}'"
            BatchManager.record_error(
                batch_id=batch.batch_id,
                error_type="UNSUPPORTED_SOURCE",
                error_message=err_msg,
                conn=conn
            )
            BatchManager.finalize_batch(
                batch_id=batch.batch_id,
                status="FAILED",
                total_rows=total_rows,
                inserted_rows=0,
                updated_rows=0,
                failed_rows=total_rows,
                error_message=err_msg,
                conn=conn
            )
            move_file(processing_path, settings.FAILED_FOLDER)
            return False

        transformed_records = []
        failed_count = 0

        for idx, row in enumerate(all_rows, start=1):
            row_valid, row_err = validate_row(source_type, row, idx)
            if not row_valid:
                failed_count += 1
                BatchManager.record_error(
                    batch_id=batch.batch_id,
                    error_type="ROW_VALIDATION_ERROR",
                    error_message=row_err,
                    row_number=idx,
                    conn=conn
                )
                continue

            # Transform row
            if source_type == "TRANSPORT":
                t_record = transformer_cls.transform_row(row, batch.batch_id, filename)
            else:
                t_record = transformer_cls.transform_row(row, batch.batch_id)

            if t_record:
                transformed_records.append(t_record)
            else:
                failed_count += 1
                BatchManager.record_error(
                    batch_id=batch.batch_id,
                    error_type="TRANSFORMATION_ERROR",
                    error_message=f"Row {idx} transformation returned None",
                    row_number=idx,
                    conn=conn
                )

        # Step 7: Perform PostgreSQL UPSERT
        inserted_updated_count = 0
        if transformed_records:
            total_affected, _ = loader_cls.upsert_batch(transformed_records, conn=conn)
            inserted_updated_count = len(transformed_records)

        # Determine batch status
        if failed_count == 0:
            final_status = "SUCCESS"
        elif len(transformed_records) > 0:
            final_status = "PARTIAL_SUCCESS"
        else:
            final_status = "FAILED"

        BatchManager.finalize_batch(
            batch_id=batch.batch_id,
            status=final_status,
            total_rows=total_rows,
            inserted_rows=inserted_updated_count,
            updated_rows=0,
            failed_rows=failed_count,
            conn=conn
        )

        # Step 8: Move file to processed directory
        move_file(processing_path, settings.PROCESSED_FOLDER)
        logger.info(f"Successfully finished batch #{batch.batch_id} for '{filename}'. Status: {final_status}")
        return True

    except Exception as e:
        logger.exception(f"Unexpected exception while processing file '{filename}': {e}")
        if batch and batch.batch_id:
            BatchManager.record_error(
                batch_id=batch.batch_id,
                error_type="PIPELINE_CRASH",
                error_message=str(e),
                conn=conn
            )
            BatchManager.finalize_batch(
                batch_id=batch.batch_id,
                status="FAILED",
                total_rows=0,
                inserted_rows=0,
                updated_rows=0,
                failed_rows=0,
                error_message=str(e),
                conn=conn
            )
            Notifier.send_alert(
                source_type="PIPELINE",
                file_name=filename,
                batch_id=batch.batch_id,
                status="FAILED",
                reason=f"Pipeline exception: {e}"
            )
        move_file(processing_path, settings.FAILED_FOLDER)
        return False

def run_pipeline(check_db: bool = True) -> int:
    """
    Main ETL sweep. Downloads files from SFTP (if enabled), finds new files, and processes each independently.
    Returns the total number of processed files.
    """
    run_entry = None
    try:
        from app.db.repositories import PipelineRunRepository
        run_entry = PipelineRunRepository.create_run("aramco_etl_sweep")
    except Exception as run_err:
        logger.debug(f"Could not record pipeline run start: {run_err}")

    # Optional SFTP Ingestion Step
    if settings.SFTP_ENABLED:
        download_files_from_sftp()

    files = discover_new_files(check_db=check_db)

    if not files:
        logger.info("No new files to process.")
        if run_entry and run_entry.run_id:
            try:
                PipelineRunRepository.finish_run(run_entry.run_id, status="SUCCESS", records_read=0, records_inserted=0)
            except Exception:
                pass
        return 0

    processed_count = 0
    for f_info in files:
        try:
            process_single_file(f_info)
            processed_count += 1
        except Exception as e:
            logger.error(f"Isolated file processing error for {f_info.file_name}: {e}")

    logger.info(f"Completed pipeline run. Processed {processed_count}/{len(files)} files.")
    if run_entry and run_entry.run_id:
        try:
            PipelineRunRepository.finish_run(run_entry.run_id, status="SUCCESS", records_read=len(files), records_inserted=processed_count)
        except Exception:
            pass

    return processed_count
