from app.loaders.base_loader import BaseLoader

class RANLoader(BaseLoader):
    table_name = "core_ran_kpi"
    conflict_columns = ["stime", "d1_plmn"]
    update_columns = [
        "s1_ho_hosr",
        "x2_ho_hosr",
        "x2_ho_attempts",
        "average_rssi_pusch",
        "erab_setup_success_rate",
        "s1_ho_attempts",
        "cell_availability",
        "erab_setup_attempts",
        "rrc_connection_setup_success_rate",
        "resource_block_utilization_ul",
        "resource_block_utilization_dl",
        "erab_drop_rate",
        "source_batch_id"
    ]
