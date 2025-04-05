import sqlite3 
import logging


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect('data/database.db')
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA busy_timeout = 30000;")
    conn.set_trace_callback(logging.debug)
    return conn