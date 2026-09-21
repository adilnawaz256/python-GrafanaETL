import sys
import time
import logging
from app.config.settings import settings
from app.etl.pipeline import run_pipeline
from app.logging.logger import logger

def run_once():
    logger.info("==========================================")
    logger.info("Starting Aramco Network Data ETL Pipeline Sweep")
    logger.info("==========================================")
    try:
        processed_count = run_pipeline(check_db=True)
        logger.info(f"ETL sweep finished cleanly. Processed {processed_count} file(s).")
    except Exception as e:
        logger.exception(f"Error executing ETL pipeline sweep: {e}")

def main():
    if settings.SINGLE_RUN:
        run_once()
        sys.exit(0)

    interval_seconds = settings.RUN_INTERVAL_SECONDS
    logger.info(f"Containerized Scheduler active. Running ETL pipeline every {interval_seconds} seconds ({interval_seconds / 60:.1f} minutes).")

    while True:
        run_once()
        logger.info(f"Sleeping for {interval_seconds} seconds until next scheduled run...")
        time.sleep(interval_seconds)

if __name__ == "__main__":
    main()
