# db_utils.py
import pyodbc
from functools import wraps
from contextlib import contextmanager

DB_CONFIG = {
    'DRIVER': '{ODBC Driver 17 for SQL Server}',
    'SERVER': 'HunterX\\SQLEXPRESS',
    'DATABASE': 'CRUD_Test',
    'UID': 'sa',
    'PWD': '43681417'
}

def get_connection_string():
    return ';'.join(f"{k}={v}" for k, v in DB_CONFIG.items())

@contextmanager
def get_db_connection():
    conn = None
    try:
        conn = pyodbc.connect(get_connection_string())
        yield conn
    finally:
        if conn:
            conn.close()

def db_operation(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        with get_db_connection() as conn:
            cursor = conn.cursor()
            try:
                result = f(cursor, *args, **kwargs)
                conn.commit()
                return result
            except Exception as e:
                conn.rollback()
                raise e
    return wrapper