import sqlite3 

import db 


conn = db.get_conn()


def get_new_messages():
    new_messages = conn.execute(
        'SELECT * FROM email_messages WHERE is_processed = 0'
    ).fetchall()
    return new_messages


def set_processed(message: sqlite3.Row):
    message_rowid = message['rowid']
    with conn:
        conn.execute(
            """
            UPDATE email_messages SET
                is_processed = 1,
                processed_timestamp = CURRENT_TIMESTAMP
            WHERE rowid = ?
            """, (message_rowid, )
        )