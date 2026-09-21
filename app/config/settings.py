import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file if present
env_path = Path(__file__).resolve().parent.parent.parent / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

class Settings:
    DATABASE_HOST: str = os.getenv("DATABASE_HOST", "localhost")
    DATABASE_PORT: int = int(os.getenv("DATABASE_PORT", "5432"))
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "aramco_etl")
    DATABASE_USER: str = os.getenv("DATABASE_USER", "postgres")
    DATABASE_PASSWORD: str = os.getenv("DATABASE_PASSWORD", "postgres")

    INPUT_FOLDER: str = os.getenv("INPUT_FOLDER", "./data/input")
    PROCESSING_FOLDER: str = os.getenv("PROCESSING_FOLDER", "./data/processing")
    PROCESSED_FOLDER: str = os.getenv("PROCESSED_FOLDER", "./data/processed")
    FAILED_FOLDER: str = os.getenv("FAILED_FOLDER", "./data/failed")
    ARCHIVE_FOLDER: str = os.getenv("ARCHIVE_FOLDER", "./data/archive")

    CRON_SCHEDULE: str = os.getenv("CRON_SCHEDULE", "*/15 * * * *")
    RUN_INTERVAL_SECONDS: int = int(os.getenv("RUN_INTERVAL_SECONDS", "900"))
    SINGLE_RUN: bool = os.getenv("SINGLE_RUN", "false").lower() in ("true", "1", "t", "yes")
    TIMEZONE: str = os.getenv("TIMEZONE", "UTC")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    BATCH_SIZE: int = int(os.getenv("BATCH_SIZE", "1000"))

    SUPPORTED_FILE_EXTENSIONS: list = os.getenv(
        "SUPPORTED_FILE_EXTENSIONS", ".xlsx,.xls,.csv"
    ).split(",")

    ALERT_ENABLED: bool = os.getenv("ALERT_ENABLED", "true").lower() in ("true", "1", "t", "yes")
    ALERT_WEBHOOK_URL: str = os.getenv("ALERT_WEBHOOK_URL", "")

    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    RETRY_DELAY_SECONDS: int = int(os.getenv("RETRY_DELAY_SECONDS", "5"))

    SFTP_ENABLED: bool = os.getenv("SFTP_ENABLED", "false").lower() in ("true", "1", "t", "yes")
    SFTP_HOST: str = os.getenv("SFTP_HOST", "")
    SFTP_PORT: int = int(os.getenv("SFTP_PORT", "22"))
    SFTP_USERNAME: str = os.getenv("SFTP_USERNAME", "")
    SFTP_PASSWORD: str = os.getenv("SFTP_PASSWORD", "")
    SFTP_KEY_FILE: str = os.getenv("SFTP_KEY_FILE", "")
    SFTP_REMOTE_DIR: str = os.getenv("SFTP_REMOTE_DIR", "/")
    SFTP_DELETE_AFTER_DOWNLOAD: bool = os.getenv("SFTP_DELETE_AFTER_DOWNLOAD", "false").lower() in ("true", "1", "t", "yes")

settings = Settings()
