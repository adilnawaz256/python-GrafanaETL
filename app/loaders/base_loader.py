import logging
from typing import List, Dict, Any, Tuple
import psycopg2.extras
from app.db.connection import get_db_connection

logger = logging.getLogger("aramco_etl.loaders")

class BaseLoader:
    table_name: str = ""
    conflict_columns: List[str] = []
    update_columns: List[str] = []

    @classmethod
    def upsert_batch(cls, records: List[Dict[str, Any]], conn=None) -> Tuple[int, int]:
        """
        Performs native PostgreSQL UPSERT for records.
        Returns:
           (inserted_count, updated_count)
        """
        if not records or not cls.table_name:
            return 0, 0

        columns = list(records[0].keys())
        cols_str = ", ".join(columns)
        conflict_str = ", ".join(cls.conflict_columns)

        # Build ON CONFLICT DO UPDATE clause
        # EXCLUDED refers to the proposed row in PostgreSQL UPSERT
        update_clauses = [f"{col} = EXCLUDED.{col}" for col in cls.update_columns if col not in cls.conflict_columns]
        update_clauses.append("updated_at = NOW()")
        update_str = ", ".join(update_clauses)

        query = f"""
            INSERT INTO {cls.table_name} ({cols_str})
            VALUES %s
            ON CONFLICT ({conflict_str})
            DO UPDATE SET {update_str};
        """

        args_list = [tuple(r[c] for c in columns) for r in records]

        def _exec(c):
            with c.cursor() as cur:
                psycopg2.extras.execute_values(cur, query, args_list)
                # In PostgreSQL execute_values does not return detailed row counts easily,
                # but returns cur.rowcount total rows affected (inserted + updated)
                total_affected = cur.rowcount
                return total_affected, 0

        if conn:
            return _exec(conn)
        with get_db_connection() as c:
            return _exec(c)
