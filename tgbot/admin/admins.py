import sqlite3 
import inspect

import db 


conn = db.get_conn()


def get_admin(user_id) -> sqlite3.Row:
    conn = db.get_conn()
    admin = conn.execute(
        'SELECT * FROM admins WHERE user_id = ?',
        (user_id, )
    ).fetchone()
    return admin 


def set_state(user_id):
    conn = db.get_conn()
    previous_frame = inspect.currentframe().f_back
    (_, _, function_name, _, _) = inspect.getframeinfo(previous_frame)
    admin = get_admin(user_id)
    if admin:
        with conn:
            conn.execute(
                'UPDATE admins SET fsm_state = ? WHERE user_id = ?', 
                (function_name, user_id)
            )
    else:
        with conn:
            conn.execute(
                'INSERT INTO admins (user_id, fsm_state) VALUES (?, ?)',
                (user_id, function_name)
            )


def get_state(user_id):
    admin = get_admin(user_id)
    if not admin:
        return None
    return admin['fsm_state']


def set_select_id(user_id, value):
    conn = db.get_conn()
    with conn:
        conn.execute(
            'UPDATE admins SET select_id = ? WHERE user_id = ?',
            (value, user_id)
        )

def get_select_id(user_id):
    admin = get_admin(user_id)
    return admin['select_id']