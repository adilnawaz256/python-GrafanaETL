from typing import Dict, Any, Optional
from app.transformation.base_transformer import BaseTransformer

class SMSCTransformer(BaseTransformer):
    @classmethod
    def transform_row(cls, row: Dict[str, Any], batch_id: int) -> Optional[Dict[str, Any]]:
        stime = cls.to_datetime(row.get("STime") or row.get("STIME"))
        hostname = cls.to_str(row.get("hostname_smsc"))

        if not stime or not hostname:
            return None

        return {
            "stime": stime,
            "hostname_smsc": hostname,
            "smsc_mt_success_rate_[%]": cls.to_float(row.get("SMSC MT Success Rate  Raw  [%]") or row.get("SMSC MT Success Rate Raw [%]")),
            "sp_mt_fail_number_[.]": cls.to_float(row.get("SP MT Fail Number  Raw  [.]") or row.get("SP MT Fail Number Raw [.]")),
            "sp_mt_success_rate_[%]": cls.to_float(row.get("SP MT Success Rate Raw  [%]") or row.get("SP MT Success Rate Raw [%]")),
            "current_speed_mt_[.]": cls.to_float(row.get("Current speed of MT Raw  [.]") or row.get("Current speed of MT Raw [.]")),
            "current_speed_mo_[.]": cls.to_float(row.get("Current speed of MO Raw  [.]") or row.get("Current speed of MO Raw [.]")),
            "used_cb_resources_[.]": cls.to_float(row.get("Number of used CB resources  Raw  [.]") or row.get("Number of used CB resources Raw [.]")),
            "total_cb_resources_[.]": cls.to_float(row.get("Total number of CB resources Raw  [.]") or row.get("Total number of CB resources Raw [.]")),
            "failure_subscriber_error_[.]": cls.to_float(row.get("Failure due to subscriber error Raw  [.]") or row.get("Failure due to subscriber error Raw [.]")),
            "failure_network_[.]": cls.to_float(row.get("Failure due to network Raw  [.]") or row.get("Failure due to network Raw [.]")),
            "memory_usage_[.]": cls.to_float(row.get("Memory usage Raw  [.]") or row.get("Memory usage Raw [.]")),
            "source_batch_id": batch_id
        }
