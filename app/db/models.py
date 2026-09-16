from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Any, Dict

@dataclass
class FileBatch:
    batch_id: Optional[int] = None
    file_name: str = ""
    file_type: str = ""
    source_type: str = ""
    file_timestamp: Optional[datetime] = None
    received_at: datetime = field(default_factory=datetime.utcnow)
    processing_started_at: Optional[datetime] = None
    processing_completed_at: Optional[datetime] = None
    status: str = "RECEIVED"
    total_rows: int = 0
    inserted_rows: int = 0
    updated_rows: int = 0
    failed_rows: int = 0
    error_message: Optional[str] = None
    file_hash: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class FileError:
    error_id: Optional[int] = None
    batch_id: int = 0
    error_type: str = ""
    error_message: str = ""
    sheet_name: Optional[str] = None
    row_number: Optional[int] = None
    column_name: Optional[str] = None
    raw_value: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class PipelineRun:
    run_id: Optional[int] = None
    batch_id: Optional[int] = None
    pipeline_name: str = ""
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    status: str = "RUNNING"
    records_read: int = 0
    records_inserted: int = 0
    records_updated: int = 0
    records_failed: int = 0
    error_message: Optional[str] = None

@dataclass
class RawRecord:
    raw_id: Optional[int] = None
    batch_id: int = 0
    source_type: str = ""
    source_file_name: str = ""
    row_number: int = 0
    raw_data: Dict[str, Any] = field(default_factory=dict)
    loaded_at: datetime = field(default_factory=datetime.utcnow)
