import sqlite3

from aiogram.types import User, Message 

import config 
import db

async def cmd_start(message: Message):
    conn = db.get_conn()

    tg_user_id = message.from_user.id
    
    manager = conn.execute(
        'SELECT * FROM managers WHERE tg_user_id = ?',
        (tg_user_id, )
    ).fetchone()    
    if manager:
        manager_name = manager['manager_name']
        await message.answer(f'Вы зарегистрированы как {manager_name}')
    else:
        await message.answer('Здравствуйте! Система вас не распознала')
    

def register_or_update_user(user: User):
    conn = db.get_conn()

    tg_user_id = user.id
    first_name = user.first_name
    last_name = user.last_name
    username = user.username 

    user_db = conn.execute(
        'SELECT * FROM users WHERE tg_user_id = ?',
        (tg_user_id, )
    ).fetchone()
    if not user_db:
        with conn:
            conn.execute(
                """
                INSERT INTO users 
                (tg_user_id, first_name, last_name, username)
                VALUES (?, ?, ?, ?)
                """, (tg_user_id, first_name, last_name, username)
            )
        
        matched_manager = conn.execute(
            'SELECT id, manager_name FROM managers WHERE tg_username = ? AND tg_user_id IS NULL',
            (username, )
        ).fetchone()
        if matched_manager:
            (manager_id, manager_name) = matched_manager
            with conn:
                conn.execute(
                    'UPDATE managers SET tg_user_id = ? WHERE id = ?',
                    (tg_user_id, manager_id)
                )
        return 

    if (first_name != user_db['first_name']
            or last_name != user_db['last_name']):
        with conn:
            conn.execute(
                """
                UPDATE users SET 
                    first_name = ?, 
                    last_name = ?,
                    updated_timestamp = CURRENT_TIMESTAMP
                WHERE tg_user_id = ?
                """, (first_name, last_name, tg_user_id)
            )

    if username != user_db['username']:
        with conn:
            conn.execute(
                """
                UPDATE users SET 
                    username = ?,
                    updated_timestamp = CURRENT_TIMESTAMP
                WHERE tg_user_id = ?
                """, (username, tg_user_id)
            )
            conn.execute(
                'UPDATE managers SET tg_username = ? WHERE tg_user_id = ?',
                (username, tg_user_id)
            )
    