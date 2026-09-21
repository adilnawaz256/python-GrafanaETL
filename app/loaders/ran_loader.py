from app.loaders.base_loader import BaseLoader

class RANLoader(BaseLoader):
    table_name = "core_ran_kpi"
    conflict_columns = ["stime", "d1_plmn"]
    update_columns = [
        "s1_ho_hosr_[%]",
        "x2_ho_hosr_[%]",
        "x2_ho_attempts_[.]",
        "average_rssi_pusch_[.]",
        "erab_setup_success_rate_[%]",
        "s1_ho_attempts_[.]",
        "cell_availability_[%]",
        "erab_setup_attempts_[.]",
        "rrc_connection_setup_success_rate_[%]",
        "resource_block_utilization_ul_[.]",
        "resource_block_utilization_dl_[.]",
        "erab_drop_rate_[%]",
        "source_batch_id"
    ]
