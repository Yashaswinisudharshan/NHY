import os
from dotenv import load_dotenv


from contextlib import contextmanager

from mysql.connector import pooling

load_dotenv()
_pool = None


def _db_config():
    return {
        "host": os.getenv("DB_HOST"),
        "port": int(os.getenv("DB_PORT")),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "database": os.getenv("DB_NAME"),
        "autocommit": False,
    }


def init_db_pool():
    global _pool
    if _pool is None:
        _pool = pooling.MySQLConnectionPool(
            pool_name="schemes_portal_pool",
            pool_size=int(os.getenv("DB_POOL_SIZE", "5")),
            **_db_config(),
        )
    return _pool


@contextmanager
def get_db_connection():
    pool = init_db_pool()
    connection = pool.get_connection()
    try:
        yield connection
    finally:
        connection.close()


@contextmanager
def get_db_cursor(dictionary=True):
    with get_db_connection() as connection:
        cursor = connection.cursor(dictionary=dictionary)
        try:
            yield connection, cursor
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            cursor.close()
