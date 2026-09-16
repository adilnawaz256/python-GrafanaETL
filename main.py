import sys
import logging
from app.etl.pipeline import run_pipeline
from app.logging.logger import logger

def main():
    logger.info("==========================================")
    logger.info("Starting Aramco Network Data ETL Pipeline")
    logger.info("==========================================")

    try:
        processed_count = run_pipeline(check_db=True)
        logger.info(f"ETL run finished cleanly. Processed {processed_count} file(s).")
    except Exception as e:
        logger.exception(f"Fatal error executing ETL pipeline: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
