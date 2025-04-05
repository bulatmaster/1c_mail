import sqlite3 

import config 
import db 


def register_message(account, from_account, uid, subject, message_date, file_paths: list):
    conn = db.get_conn()
    with conn:
        conn.execute(
            """
            INSERT INTO email_messages
            (account, from_account, message_uid, message_subject, message_date)
            VALUES (?, ?, ?, ?, ?)
            """, (account, from_account, uid, subject, message_date)
        )
        (message_rowid, ) = conn.execute(
            'SELECT last_insert_rowid() FROM email_messages'
        ).fetchone()
        for file_path in file_paths:
            conn.execute(
                """
                INSERT INTO email_files
                (message_rowid, file_path)
                VALUES (?, ?)
                """, (message_rowid, file_path)
            )
    conn.close()


def is_message_processed(account, uid):
    conn = db.get_conn()
    message = conn.execute(
        'SELECT * FROM email_messages WHERE account = ? AND message_uid = ?',
        (account, uid)
    ).fetchone()
    conn.close()
    return bool(message)