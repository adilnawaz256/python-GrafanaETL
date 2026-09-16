from typing import Dict, Any, Optional
from app.transformation.base_transformer import BaseTransformer

class AlarmTransformer(BaseTransformer):
    @classmethod
    def transform_row(cls, row: Dict[str, Any], batch_id: int) -> Optional[Dict[str, Any]]:
        alarm_id = cls.to_str(row.get("Alarm ID"))
        event_time = cls.to_datetime(row.get("Event Time"))

        if not alarm_id or not event_time:
            return None

        return {
            "alarm_id": alarm_id,
            "notification_identifier": cls.to_str(row.get("Notification Identifier")),
            "original_severity": cls.to_str(row.get("Original Severity")),
            "perceived_severity": cls.to_str(row.get("Perceived Severity")),
            "cleared": cls.to_bool(row.get("Cleared")),
            "creation_time": cls.to_datetime(row.get("Creation Time")),
            "clear_time": cls.to_datetime(row.get("Clear Time")),
            "acknowledge_state": cls.to_str(row.get("Acknowledge State")),
            "mo_identifier": cls.to_str(row.get("MO Identifier")),
            "specific_problem": cls.to_str(row.get("Specific Problem")),
            "additional_text": cls.to_str(row.get("Additional Text")),
            "mo_tt_info": cls.to_str(row.get("MO TT Info")),
            "note": cls.to_str(row.get("Note")),
            "event_time": event_time,
            "update_time": cls.to_datetime(row.get("Update Time")),
            "adapter_name": cls.to_str(row.get("Adapter Name")),
            "event_action_log": cls.to_str(row.get("Event Action Log")),
            "event_qualification": cls.to_str(row.get("Event Qualification")),
            "correlated_notifications": cls.to_str(row.get("Correlated Notifications")),
            "probable_cause": cls.to_str(row.get("Probable Cause")),
            "acknowledge_time": cls.to_datetime(row.get("Acknowledge Time")),
            "acknowledge_user_id": cls.to_str(row.get("Acknowledge User ID")),
            "managed_object_instance": cls.to_str(row.get("Managed Object Instance")),
            "alert_count": cls.to_int(row.get("Alert Count")),
            "first_acknowledge_time": cls.to_datetime(row.get("First Acknowledge Time")),
            "sla_priority": cls.to_str(row.get("SLA Priority")),
            "tt_time": cls.to_datetime(row.get("TT Time")),
            "source_batch_id": batch_id
        }
