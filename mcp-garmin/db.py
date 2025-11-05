import sqlite3
import os
from contextlib import contextmanager

# The database path is set to the absolute path where the Docker volume is mounted
DB_PATH = os.getenv("SQLITE_PATH", "/data/mesh.db")

@contextmanager
def db() -> sqlite3.Connection:
    """
    Provides a database connection context manager for the garmin service
    to interact with the shared mesh database.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()
