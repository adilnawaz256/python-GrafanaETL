from app.loaders.base_loader import BaseLoader

class AlarmLoader(BaseLoader):
    table_name = "core_alarms"
    conflict_columns = ["alarm_id", "event_time"]
    update_columns = [
        "notification_identifier",
        "original_severity",
        "perceived_severity",
        "cleared",
        "creation_time",
        "clear_time",
        "acknowledge_state",
        "mo_identifier",
        "specific_problem",
        "additional_text",
        "mo_tt_info",
        "note",
        "update_time",
        "adapter_name",
        "event_action_log",
        "event_qualification",
        "correlated_notifications",
        "probable_cause",
        "acknowledge_time",
        "acknowledge_user_id",
        "managed_object_instance",
        "alert_count",
        "first_acknowledge_time",
        "sla_priority",
        "tt_time",
        "source_batch_id"
    ]
