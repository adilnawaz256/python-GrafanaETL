import os
import logging
from pathlib import Path
from typing import List
from app.config.settings import settings

logger = logging.getLogger("aramco_etl.sftp")

def download_files_from_sftp() -> List[str]:
    """
    Connects to the configured remote SFTP server and downloads supported files (.csv, .xlsx, .xls)
    into the local INPUT_FOLDER directory. Returns a list of downloaded local file paths.
    """
    if not settings.SFTP_ENABLED:
        logger.debug("SFTP ingestion is disabled (SFTP_ENABLED=false).")
        return []

    if not settings.SFTP_HOST or not settings.SFTP_USERNAME:
        logger.warning("SFTP is enabled but SFTP_HOST or SFTP_USERNAME is not configured.")
        return []

    try:
        import paramiko
    except ImportError:
        logger.error("paramiko library is not installed. Install paramiko to use SFTP ingestion.")
        return []

    downloaded_files: List[str] = []
    target_dir = Path(settings.INPUT_FOLDER)
    target_dir.mkdir(parents=True, exist_ok=True)

    supported_exts = set(ext.strip().lower() for ext in settings.SUPPORTED_FILE_EXTENSIONS)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        host = settings.SFTP_HOST.strip()
        username = settings.SFTP_USERNAME.strip()
        password = settings.SFTP_PASSWORD.strip() if settings.SFTP_PASSWORD else ""

        logger.info(f"Connecting to SFTP server {host}:{settings.SFTP_PORT} as '{username}'...")
        
        connect_kwargs = {
            "hostname": host,
            "port": settings.SFTP_PORT,
            "username": username,
            "timeout": 30,
        }

        if settings.SFTP_KEY_FILE and os.path.exists(settings.SFTP_KEY_FILE.strip()):
            connect_kwargs["key_filename"] = settings.SFTP_KEY_FILE.strip()
        elif password:
            connect_kwargs["password"] = password

        ssh.connect(**connect_kwargs)
        sftp = ssh.open_sftp()

        remote_dir = settings.SFTP_REMOTE_DIR.strip() if settings.SFTP_REMOTE_DIR else "."
        try:
            sftp.chdir(remote_dir)
        except Exception:
            pass
        file_list = sftp.listdir()

        logger.info(f"Scanning remote SFTP directory '{remote_dir}'. Found {len(file_list)} remote item(s).")

        for filename in file_list:
            ext = os.path.splitext(filename)[1].lower()
            if ext in supported_exts:
                local_path = os.path.join(str(target_dir), filename)
                remote_path = f"{remote_dir.rstrip('/')}/{filename}"
                
                logger.info(f"Downloading remote SFTP file '{filename}' -> '{local_path}'...")
                sftp.get(remote_path, local_path)
                downloaded_files.append(local_path)

                if settings.SFTP_DELETE_AFTER_DOWNLOAD:
                    logger.info(f"Deleting downloaded file '{remote_path}' from remote SFTP server...")
                    sftp.remove(remote_path)

        sftp.close()
        ssh.close()
        logger.info(f"SFTP download complete. Downloaded {len(downloaded_files)} file(s).")

    except Exception as e:
        logger.error(f"Error occurred during SFTP download from {settings.SFTP_HOST}: {e}")

    return downloaded_files
