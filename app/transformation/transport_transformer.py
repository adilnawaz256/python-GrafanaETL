import re
from typing import Dict, Any, Optional
from app.transformation.base_transformer import BaseTransformer

class TransportTransformer(BaseTransformer):
    @classmethod
    def extract_device_name_from_filename(cls, filename: str) -> str:
        match = re.search(r'transport_(.*?)-\d{4}-\d{2}-\d{2}', filename, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        clean = filename.replace(".csv", "").replace(".xlsx", "").replace(".xls", "")
        clean = re.sub(r'^transport_', '', clean, flags=re.IGNORECASE)
        return clean

    @classmethod
    def transform_row(cls, row: Dict[str, Any], batch_id: int, filename: str) -> Optional[Dict[str, Any]]:
        stime = cls.to_datetime(row.get("STime") or row.get("STIME"))
        n_interface = cls.to_str(row.get("n_interface"))
        device_name = cls.extract_device_name_from_filename(filename)

        if not stime or not n_interface or not device_name:
            return None

        return {
            "stime": stime,
            "device_name": device_name,
            "n_interface": n_interface,
            "utilization_out_[%]": cls.to_float(row.get("Utilization Out Raw  [%]") or row.get("Utilization Out Raw [%]")),
            "utilization_in_[%]": cls.to_float(row.get("Utilization In Raw  [%]") or row.get("Utilization In Raw [%]")),
            "source_batch_id": batch_id
        }
