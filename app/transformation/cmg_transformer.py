from typing import Dict, Any, Optional
from app.transformation.base_transformer import BaseTransformer

class CMGTransformer(BaseTransformer):
    @classmethod
    def transform_row(cls, row: Dict[str, Any], batch_id: int) -> Optional[Dict[str, Any]]:
        stime = cls.to_datetime(row.get("STime") or row.get("STIME"))
        cmg = cls.to_str(row.get("cmg_1") or row.get("cmg"))

        if not stime or not cmg:
            return None

        return {
            "stime": stime,
            "cmg": cmg,
            "total_data_throughput_mbps": cls.to_float(row.get("Total Data Throughput Raw  [Mb/s]") or row.get("Total Data Throughput Raw [Mb/s]")),
            "s11_create_session_success_ratio_[%]": cls.to_float(row.get("S11 Create Session received success ratio Raw  [%]") or row.get("S11 Create Session received success ratio Raw [%]")),
            "total_data_volume_mb": cls.to_float(row.get("Total data volume Raw  [MB]") or row.get("Total data volume Raw [MB]")),
            "source_batch_id": batch_id
        }
