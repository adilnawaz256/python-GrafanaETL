from app.loaders.base_loader import BaseLoader

class SMSCLoader(BaseLoader):
    table_name = "core_smsc_kpi"
    conflict_columns = ["stime", "hostname_smsc"]
    update_columns = [
        "smsc_mt_success_rate_[%]",
        "sp_mt_fail_number_[.]",
        "sp_mt_success_rate_[%]",
        "current_speed_mt_[.]",
        "current_speed_mo_[.]",
        "used_cb_resources_[.]",
        "total_cb_resources_[.]",
        "failure_subscriber_error_[.]",
        "failure_network_[.]",
        "memory_usage_[.]",
        "source_batch_id"
    ]
