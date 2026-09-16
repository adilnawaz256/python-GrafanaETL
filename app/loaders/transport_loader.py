from app.loaders.base_loader import BaseLoader

class TransportLoader(BaseLoader):
    table_name = "core_transport_kpi"
    conflict_columns = ["stime", "device_name", "n_interface"]
    update_columns = [
        "utilization_out",
        "utilization_in",
        "source_batch_id"
    ]
