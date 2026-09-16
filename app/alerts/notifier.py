import logging
from typing import Dict, Any, Optional
import requests
from app.config.settings import settings

logger = logging.getLogger("aramco_etl.alerts")

class Notifier:
    @staticmethod
    def send_alert(
        source_type: str,
        file_name: str,
        batch_id: Optional[int],
        status: str,
        reason: str,
        details: Optional[Dict[str, Any]] = None
    ):
        alert_msg = (
            f"ETL Alert\n"
            f"Source: {source_type}\n"
            f"File: {file_name}\n"
            f"Batch: {batch_id or 'N/A'}\n"
            f"Status: {status}\n"
            f"Reason: {reason}"
        )
        logger.warning(f"ALERT TRIGGERED:\n{alert_msg}")

        if not settings.ALERT_ENABLED or not settings.ALERT_WEBHOOK_URL:
            logger.info("Webhook alerts disabled or URL missing.")
            return

        payload = {
            "text": alert_msg,
            "source": source_type,
            "file": file_name,
            "batch_id": batch_id,
            "status": status,
            "reason": reason,
            "details": details or {}
        }

        try:
            response = requests.post(settings.ALERT_WEBHOOK_URL, json=payload, timeout=5)
            if response.status_code >= 400:
                logger.error(f"Failed to post alert webhook: {response.status_code} - {response.text}")
            else:
                logger.info("Successfully sent alert webhook.")
        except Exception as e:
            logger.error(f"Error sending alert webhook to {settings.ALERT_WEBHOOK_URL}: {e}")
