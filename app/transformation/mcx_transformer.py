from typing import Dict, Any, Optional
from app.transformation.base_transformer import BaseTransformer

class MCXTransformer(BaseTransformer):
    @classmethod
    def transform_row(cls, row: Dict[str, Any], batch_id: int) -> Optional[Dict[str, Any]]:
        stime = cls.to_datetime(row.get("STime") or row.get("STIME"))
        network = cls.to_str(row.get("centreon_network") or row.get("CENTREON_NETWORK") or "Aramco")

        if not stime or not network:
            return None

        return {
            "stime": stime,
            "centreon_network": network,
            "kpi1_3gpp_mcptt_access_time_avg_[.]": cls.to_float(row.get("kpi1_3gpp_mcptt_access_time_avg Raw  [.]") or row.get("kpi1_3gpp_mcptt_access_time_avg Raw [.]")),
            "kpi1_3gpp_mcptt_access_time_min_[.]": cls.to_float(row.get("kpi1_3gpp_mcptt_access_time_min Raw  [.]") or row.get("kpi1_3gpp_mcptt_access_time_min Raw [.]")),
            "kpi1_3gpp_mcptt_access_time_max_[.]": cls.to_float(row.get("kpi1_3gpp_mcptt_access_time_max Raw  [.]") or row.get("kpi1_3gpp_mcptt_access_time_max Raw [.]")),
            "kpi3_3gpp_mouth_to_ear_latency_avg_[.]": cls.to_float(row.get("kpi3_3gpp_mouth_to_ear_latency_avg Raw  [.]") or row.get("kpi3_3gpp_mouth_to_ear_latency_avg Raw [.]")),
            "kpi3_3gpp_mouth_to_ear_latency_min_[.]": cls.to_float(row.get("kpi3_3gpp_mouth_to_ear_latency_min Raw  [.]") or row.get("kpi3_3gpp_mouth_to_ear_latency_min Raw [.]")),
            "kpi2_3gpp_mcptt_access_time_end_to_end_max_[.]": cls.to_float(row.get("kpi2_3gpp_mcptt_access_time_end_to_end_max Raw  [.]") or row.get("kpi2_3gpp_mcptt_access_time_end_to_end_max Raw [.]")),
            "kpi3_3gpp_mouth_to_ear_latency_max_[.]": cls.to_float(row.get("kpi3_3gpp_mouth_to_ear_latency_max Raw  [.]") or row.get("kpi3_3gpp_mouth_to_ear_latency_max Raw [.]")),
            "kpi2_3gpp_mcptt_access_time_end_to_end_avg_[.]": cls.to_float(row.get("kpi2_3gpp_mcptt_access_time_end_to_end_avg Raw  [.]") or row.get("kpi2_3gpp_mcptt_access_time_end_to_end_avg Raw [.]")),
            "kpi2_3gpp_mcptt_access_time_end_to_end_min_[.]": cls.to_float(row.get("kpi2_3gpp_mcptt_access_time_end_to_end_min Raw  [.]") or row.get("kpi2_3gpp_mcptt_access_time_end_to_end_min Raw [.]")),
            "source_batch_id": batch_id
        }
