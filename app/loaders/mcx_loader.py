from app.loaders.base_loader import BaseLoader

class MCXLoader(BaseLoader):
    table_name = "core_mcx_kpi"
    conflict_columns = ["stime", "centreon_network"]
    update_columns = [
        "kpi1_3gpp_mcptt_access_time_avg_[.]",
        "kpi1_3gpp_mcptt_access_time_min_[.]",
        "kpi1_3gpp_mcptt_access_time_max_[.]",
        "kpi3_3gpp_mouth_to_ear_latency_avg_[.]",
        "kpi3_3gpp_mouth_to_ear_latency_min_[.]",
        "kpi2_3gpp_mcptt_access_time_end_to_end_max_[.]",
        "kpi3_3gpp_mouth_to_ear_latency_max_[.]",
        "kpi2_3gpp_mcptt_access_time_end_to_end_avg_[.]",
        "kpi2_3gpp_mcptt_access_time_end_to_end_min_[.]",
        "source_batch_id"
    ]
