from app.loaders.base_loader import BaseLoader

class CMGLoader(BaseLoader):
    table_name = "core_cmg_kpi"
    conflict_columns = ["stime", "cmg"]
    update_columns = [
        "total_data_throughput_mbps",
        "s11_create_session_success_ratio_[%]",
        "total_data_volume_mb",
        "source_batch_id"
    ]
