from typing import Dict, Any, Optional
from app.transformation.base_transformer import BaseTransformer

class IMSTransformer(BaseTransformer):
    @classmethod
    def transform_row(cls, row: Dict[str, Any], batch_id: int) -> Optional[Dict[str, Any]]:
        stime = cls.to_datetime(row.get("STIME") or row.get("STime"))
        cscf = cls.to_str(row.get("cscf"))

        if not stime or not cscf:
            return None

        return {
            "stime": stime,
            "cscf": cscf,
            "call_setup_time": cls.to_float(row.get("Call Setup Time")),
            "initial_registration_success_rate": cls.to_float(row.get("Initial Registration Success Rate")),
            "session_setup_time": cls.to_float(row.get("Session Setup Time")),
            "mo_session_attempts": cls.to_float(row.get("Number of S-CSCF mo session attempts")),
            "mt_session_attempts": cls.to_float(row.get("Number of S-CSCF mt session attempts")),
            "registered_users": cls.to_float(row.get("Number of S-CSCF registered users")),
            "source_batch_id": batch_id
        }
