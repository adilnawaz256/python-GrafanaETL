import pytest
from app.alerts.notifier import Notifier
from app.config.settings import settings

def test_alert_notifier_logs_without_crashing(monkeypatch):
    monkeypatch.setattr(settings, "ALERT_ENABLED", True)
    monkeypatch.setattr(settings, "ALERT_WEBHOOK_URL", "")

    # Should not raise exception
    Notifier.send_alert(
        source_type="RAN",
        file_name="RAN-2026-09-14T141500.csv",
        batch_id=1025,
        status="FAILED",
        reason="Missing required column Cell Availability Raw [%]"
    )
