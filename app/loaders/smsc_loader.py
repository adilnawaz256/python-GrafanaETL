from app.loaders.base_loader import BaseLoader

class SMSCLoader(BaseLoader):
    table_name = "core_smsc_kpi"
    conflict_columns = ["stime", "hostname_smsc"]
    update_columns = [
        "smsc_mt_success_rate",
        "sp_mt_fail_number",
        "sp_mt_success_rate",
        "current_speed_mt",
        "current_speed_mo",
        "used_cb_resources",
        "total_cb_resources",
        "failure_subscriber_error",
        "failure_network",
        "memory_usage",
        "source_batch_id"
    ]
