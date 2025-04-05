import sqlite3 
import inspect 

from aiogram import Bot 
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup

import db 


def get_admin(user_id) -> sqlite3.Row:
    conn = db.get_conn()
    admin = conn.execute(
        'SELECT * FROM admins WHERE tg_user_id = ?',
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
                'UPDATE admins SET fsm_state = ? WHERE tg_user_id = ?', 
                (function_name, user_id)
            )
    else:
        with conn:
            conn.execute(
                'INSERT INTO admins (tg_user_id, fsm_state) VALUES (?, ?)',
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
            'UPDATE admins SET select_id = ? WHERE tg_user_id = ?',
            (value, user_id)
        )

def get_select_id(user_id):
    admin = get_admin(user_id)
    return admin['select_id']


def kb(*buttons: str, row_size=2) -> ReplyKeyboardMarkup:
    """
    Генерирует клавиатуру с кнопками.
    
    :param buttons: Произвольное количество текстов кнопок
    :return: Объект ReplyKeyboardMarkup с заданными параметрами
    """
    builder = ReplyKeyboardBuilder()

    for button_text in buttons:
        builder.button(text=button_text)
    
    # Можно добавить логику для автонастройки количества кнопок в строке
    builder.adjust(row_size)  # Настраиваем количество кнопок в строке

    # Создаем и возвращаем клавиатуру с нужными параметрами
    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=False,
    )

