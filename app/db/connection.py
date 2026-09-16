import logging
from contextlib import contextmanager
import psycopg2
from psycopg2.pool import ThreadedConnectionPool
from app.config.settings import settings

logger = logging.getLogger("aramco_etl.db")

_pool = None

def get_pool():
    global _pool
    if _pool is None:
        try:
            _pool = ThreadedConnectionPool(
                minconn=1,
                maxconn=10,
                host=settings.DATABASE_HOST,
                port=settings.DATABASE_PORT,
                dbname=settings.DATABASE_NAME,
                user=settings.DATABASE_USER,
                password=settings.DATABASE_PASSWORD
            )
            logger.info("Initialized PostgreSQL connection pool.")
        except Exception as e:
            logger.error(f"Failed to initialize PostgreSQL connection pool: {e}")
            raise
    return _pool

@contextmanager
def get_db_connection():
    """
    Context manager providing a database connection from the pool.
    Commits on success, rolls back on exception, and returns connection to pool.
    """
    pool = get_pool()
    conn = pool.getconn()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        pool.putconn(conn)

def close_pool():
    global _pool
    if _pool is not None:
        _pool.closeall()
        _pool = None
        logger.info("Closed PostgreSQL connection pool.")
