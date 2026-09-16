from typing import Dict, Any, Optional
from app.transformation.base_transformer import BaseTransformer

class RANTransformer(BaseTransformer):
    @classmethod
    def transform_row(cls, row: Dict[str, Any], batch_id: int) -> Optional[Dict[str, Any]]:
        stime = cls.to_datetime(row.get("STime") or row.get("STIME"))
        d1_plmn = cls.to_str(row.get("d1_plmn"))

        if not stime or not d1_plmn:
            return None

        return {
            "stime": stime,
            "d1_plmn": d1_plmn,
            "s1_ho_hosr": cls.to_float(row.get("S1 HO HOSR Raw  [%]") or row.get("S1 HO HOSR Raw [%]")),
            "x2_ho_hosr": cls.to_float(row.get("X2 HO HOSR Raw  [%]") or row.get("X2 HO HOSR Raw [%]")),
            "x2_ho_attempts": cls.to_float(row.get("X2 HO Attempts Raw  [.]") or row.get("X2 HO Attempts Raw [.]")),
            "average_rssi_pusch": cls.to_float(row.get("Average RSSI for PUSCH Raw  [.]") or row.get("Average RSSI for PUSCH Raw [.]")),
            "erab_setup_success_rate": cls.to_float(row.get("E-RAB Setup Success Rate Raw  [%]") or row.get("E-RAB Setup Success Rate Raw [%]")),
            "s1_ho_attempts": cls.to_float(row.get("S1 HO Attempts Raw  [.]") or row.get("S1 HO Attempts Raw [.]")),
            "cell_availability": cls.to_float(row.get("Cell Availability Raw  [%]") or row.get("Cell Availability Raw [%]")),
            "erab_setup_attempts": cls.to_float(row.get("E-RAB Setup Attempts Raw  [.]") or row.get("E-RAB Setup Attempts Raw [.]")),
            "rrc_connection_setup_success_rate": cls.to_float(row.get("RRC Connection Setup Success Rate Raw  [%]") or row.get("RRC Connection Setup Success Rate Raw [%]")),
            "resource_block_utilization_ul": cls.to_float(row.get("Resource Block Utilization (UL) Raw  [.]") or row.get("Resource Block Utilization (UL) Raw [.]")),
            "resource_block_utilization_dl": cls.to_float(row.get("Resource Block Utilization (DL) Raw  [.]") or row.get("Resource Block Utilization (DL) Raw [.]")),
            "erab_drop_rate": cls.to_float(row.get("E-RAB Drop Rate Raw  [%]") or row.get("E-RAB Drop Rate Raw [%]")),
            "source_batch_id": batch_id
        }
