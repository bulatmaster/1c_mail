from aiogram.types import User 

import db 


conn = db.get_conn()


def register_or_update_user(user: User) -> bool:
    """
    Регистрирует/обновляет пользователя в ДБ ,
    Возвращает был ли пользователь новым пользователем
    """

    user_id = user.id
    first_name = user.first_name
    last_name = user.last_name
    username = user.username 

    user_exists = conn.execute(
        'SELECT * FROM tg_users WHERE user_id = ?',
        (user_id, )
    ).fetchone()
    
    if user_exists:
        with conn:
            conn.execute(
                """
                UPDATE tg_users SET 
                    first_name = ?, 
                    last_name = ?,
                    username = ?,
                    last_message_timestamp = CURRENT_TIMESTAMP
                WHERE user_id = ?
                """, (first_name, last_name, username, user_id)
            )
        return False

    else:
        with conn:
            conn.execute(
                """
                INSERT INTO tg_users 
                (user_id, first_name, last_name, username)
                VALUES (?, ?, ?, ?)
                """, (user_id, first_name, last_name, username)
            )
        return True


def get_user(user_id):
    return conn.execute(
        'SELECT * FROM tg_users WHERE user_id = ?',
        (user_id, )
    ).fetchone()
    

def save_organization_name(user_id, organization_name):
    with conn:
        conn.execute(
            """
            UPDATE tg_users SET 
                organization_name = ?,
                request_timestamp = CURRENT_TIMESTAMP 
            WHERE user_id = ?
            """, 
            (organization_name, user_id)
        )

