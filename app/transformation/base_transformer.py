from typing import Optional, Any
from datetime import datetime
from app.utils.timestamps import parse_datetime

class BaseTransformer:
    @staticmethod
    def to_float(val: Any) -> Optional[float]:
        if val is None:
            return None
        val_str = str(val).strip()
        if not val_str or val_str.lower() in ("nan", "none", "null", "n/a", ""):
            return None
        try:
            return float(val_str)
        except ValueError:
            return None

    @staticmethod
    def to_int(val: Any) -> Optional[int]:
        f = BaseTransformer.to_float(val)
        return int(f) if f is not None else None

    @staticmethod
    def to_datetime(val: Any) -> Optional[datetime]:
        return parse_datetime(val)

    @staticmethod
    def to_bool(val: Any) -> Optional[bool]:
        if val is None:
            return None
        if isinstance(val, bool):
            return val
        val_str = str(val).strip().lower()
        if val_str in ("true", "1", "t", "yes", "y"):
            return True
        elif val_str in ("false", "0", "f", "no", "n"):
            return False
        return None

    @staticmethod
    def to_str(val: Any) -> Optional[str]:
        if val is None:
            return None
        val_str = str(val).strip()
        return val_str if val_str and val_str.lower() not in ("nan", "none", "null") else None
