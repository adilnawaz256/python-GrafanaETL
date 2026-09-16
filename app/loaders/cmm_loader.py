from app.loaders.base_loader import BaseLoader

class CMMLoader(BaseLoader):
    table_name = "core_cmm_kpi"
    conflict_columns = ["stime", "cmm"]
    update_columns = [
        "eps_attach_success_ratio",
        "eps_service_request_success_ratio",
        "eps_ps_paging_success_ratio",
        "source_batch_id"
    ]
