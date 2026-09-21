from app.loaders.base_loader import BaseLoader

class TransportLoader(BaseLoader):
    table_name = "core_transport_kpi"
    conflict_columns = ["stime", "device_name", "n_interface"]
    update_columns = [
        "utilization_out_[%]",
        "utilization_in_[%]",
        "source_batch_id"
    ]
