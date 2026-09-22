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

    supported_exts = tuple(ext.strip().lower() for ext in settings.SUPPORTED_FILE_EXTENSIONS if ext.strip())

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

        # List of directories to search
        search_dirs = [remote_dir]
        for fallback in [".", "/", "/files", "/upload"]:
            if fallback not in search_dirs:
                search_dirs.append(fallback)

        found_remote_files = [] # list of (remote_path, filename)

        for s_dir in search_dirs:
            try:
                items = sftp.listdir_attr(s_dir)
                logger.info(f"Directory '{s_dir}' raw file list: {[item.filename for item in items]}")
                for item in items:
                    fname = item.filename
                    clean_fname = fname.strip()
                    clean_fname_lower = clean_fname.lower()

                    is_supported = clean_fname_lower.endswith(supported_exts) or any(ext in clean_fname_lower for ext in ('.csv', '.xlsx', '.xls'))

                    if is_supported:
                        r_path = f"{s_dir.rstrip('/')}/{fname}" if s_dir not in (".", "") else fname
                        if (r_path, fname) not in found_remote_files:
                            found_remote_files.append((r_path, fname))
                    elif (item.st_mode is not None and (item.st_mode & 0o040000)) or fname in ("files", "upload", "data"):
                        sub_dir = f"{s_dir.rstrip('/')}/{fname}" if s_dir not in (".", "") else fname
                        try:
                            sub_items = sftp.listdir_attr(sub_dir)
                            logger.info(f"Subdirectory '{sub_dir}' raw file list: {[i.filename for i in sub_items]}")
                            for sub_item in sub_items:
                                sub_fname = sub_item.filename
                                sub_lower = sub_fname.strip().lower()
                                if sub_lower.endswith(supported_exts) or any(ext in sub_lower for ext in ('.csv', '.xlsx', '.xls')):
                                    sub_r_path = f"{sub_dir.rstrip('/')}/{sub_fname}"
                                    if (sub_r_path, sub_fname) not in found_remote_files:
                                        found_remote_files.append((sub_r_path, sub_fname))
                        except Exception as sub_err:
                            logger.debug(f"Could not list subdirectory {sub_dir}: {sub_err}")
            except Exception as dir_err:
                logger.debug(f"Could not list directory {s_dir}: {dir_err}")

            if found_remote_files:
                logger.info(f"Found {len(found_remote_files)} supported file(s) in SFTP directory '{s_dir}'.")
                break

        if not found_remote_files:
            logger.info("Scanning SFTP directories completed. Found 0 supported file(s).")

        for remote_path, filename in found_remote_files:
            local_path = os.path.join(str(target_dir), filename)
            logger.info(f"Downloading remote SFTP file '{remote_path}' -> '{local_path}'...")
            try:
                sftp.get(remote_path, local_path)
                downloaded_files.append(local_path)

                if settings.SFTP_DELETE_AFTER_DOWNLOAD:
                    logger.info(f"Deleting downloaded file '{remote_path}' from remote SFTP server...")
                    sftp.remove(remote_path)
            except Exception as download_err:
                logger.error(f"Failed to download remote file '{remote_path}': {download_err}")

        sftp.close()
        ssh.close()
        logger.info(f"SFTP download complete. Downloaded {len(downloaded_files)} file(s).")

    except Exception as e:
        logger.error(f"Error occurred during SFTP download from {settings.SFTP_HOST}: {e}")

    return downloaded_files
