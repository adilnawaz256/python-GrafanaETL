from typing import Dict, Any, Optional
from app.transformation.base_transformer import BaseTransformer

class CMMTransformer(BaseTransformer):
    @classmethod
    def transform_row(cls, row: Dict[str, Any], batch_id: int) -> Optional[Dict[str, Any]]:
        stime = cls.to_datetime(row.get("STime") or row.get("STIME"))
        cmm = cls.to_str(row.get("cmm"))

        if not stime or not cmm:
            return None

        return {
            "stime": stime,
            "cmm": cmm,
            "eps_attach_success_ratio": cls.to_float(row.get('EPS attach "technical" success ratio Raw  [%]') or row.get('EPS attach "technical" success ratio Raw [%]')),
            "eps_service_request_success_ratio": cls.to_float(row.get("EPS Service Request success ratio Raw  [%]") or row.get("EPS Service Request success ratio Raw [%]")),
            "eps_ps_paging_success_ratio": cls.to_float(row.get("EPS PS Paging success ratio Raw  [%]") or row.get("EPS PS Paging success ratio Raw [%]")),
            "source_batch_id": batch_id
        }
