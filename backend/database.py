"""
Database connection module using mysql-connector-python connection pooling.
"""

import mysql.connector
from mysql.connector import pooling
from config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME


# ── Connection Pool ────────────────────────────────────────────────────────────
_pool = None


def get_pool():
    """Lazy-initialise and return the connection pool."""
    global _pool
    if _pool is None:
        _pool = pooling.MySQLConnectionPool(
            pool_name="egov_pool",
            pool_size=10,
            pool_reset_session=True,
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            charset="utf8mb4",
            collation="utf8mb4_unicode_ci",
            autocommit=False,
        )
    return _pool


def get_db():
    """
    FastAPI dependency — yields a database connection from the pool.
    Automatically commits on success and rolls back on error.
    """
    pool = get_pool()
    conn = pool.get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def execute_query(conn, query: str, params: tuple = None, fetch: str = "all"):
    """
    Utility to execute a query and return results.

    Parameters
    ----------
    conn   : MySQL connection
    query  : SQL query string
    params : Query parameters (tuple)
    fetch  : 'all' | 'one' | 'none'

    Returns
    -------
    List[dict] | dict | None
    """
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, params)

    if fetch == "all":
        result = cursor.fetchall()
    elif fetch == "one":
        result = cursor.fetchone()
    else:
        result = None

    cursor.close()
    return result


def execute_procedure(conn, proc_name: str, args: tuple):
    """
    Execute a stored procedure and return results + out parameters.
    """
    cursor = conn.cursor(dictionary=True)
    result_args = cursor.callproc(proc_name, args)
    results = []
    for result_set in cursor.stored_results():
        results.append(result_set.fetchall())
    cursor.close()
    return results, result_args
