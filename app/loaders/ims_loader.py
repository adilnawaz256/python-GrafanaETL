from app.loaders.base_loader import BaseLoader

class IMSLoader(BaseLoader):
    table_name = "core_ims_kpi"
    conflict_columns = ["stime", "cscf"]
    update_columns = [
        "call_setup_time",
        "initial_registration_success_rate",
        "session_setup_time",
        "mo_session_attempts",
        "mt_session_attempts",
        "registered_users",
        "source_batch_id"
    ]
