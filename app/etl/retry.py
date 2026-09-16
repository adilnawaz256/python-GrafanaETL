import time
import logging
from typing import Callable, Any, Optional
from app.config.settings import settings

logger = logging.getLogger("aramco_etl.retry")

def retry_operation(
    func: Callable[[], Any],
    max_retries: Optional[int] = None,
    delay_seconds: Optional[int] = None,
    operation_name: str = "Operation"
) -> Any:
    retries = max_retries if max_retries is not None else settings.MAX_RETRIES
    delay = delay_seconds if delay_seconds is not None else settings.RETRY_DELAY_SECONDS

    last_exception: Optional[Exception] = None
    for attempt in range(1, retries + 1):
        try:
            return func()
        except Exception as e:
            last_exception = e
            logger.warning(
                f"{operation_name} failed attempt {attempt}/{retries}: {e}. Retrying in {delay}s..."
            )
            if attempt < retries:
                time.sleep(delay)

    logger.error(f"{operation_name} permanently failed after {retries} attempts.")
    if last_exception is not None:
        raise last_exception
    raise RuntimeError(f"{operation_name} failed after {retries} attempts without an exception.")

