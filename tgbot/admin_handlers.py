import re
import sqlite3
from datetime import datetime, timezone, timedelta
from pathlib import Path
import random 
import inspect
import os 

import aiogram 
from aiogram import Bot, html
from aiogram.types import Message, ReplyKeyboardRemove

from tgbot.admin_utils import kb, set_state, get_select_id, set_select_id
import config
import db 


async def main_menu(bot, user_id):
    conn = db.get_conn()
    emails = '_'
    receivers = '_'
    (total_managers, ) = conn.execute('SELECT COUNT(*) FROM managers').fetchone()
    managers_no_username = conn.execute(
        'SELECT manager_name FROM managers WHERE tg_username IS NULL'
    ).fetchall()
    answer = (
        f'- Главное меню -\n'
        f'\n'
        f'Сегодня получено {emails} писем и распределено по {receivers} менеджерам\n'
        f'\n'
        f'В системе всего {total_managers} менеджеров \n'
        f'\n'
    )
    for (name, ) in managers_no_username:
        answer += f'❗️ Для менеджера {name} не указан юзернейм \n\n'

    keyboard = kb('👤 Менеджеры')

    await bot.send_message(user_id, answer, reply_markup=keyboard)
    set_state(user_id)


async def managers_menu(bot, user_id):
    conn = db.get_conn()
    managers = conn.execute('SELECT * FROM managers').fetchall()
    answer = f'- Управление менеджерами -\n\n'
    for manager in managers:
        manager_id = manager['id']
        name = manager['manager_name']
        username = manager['tg_username']
        tg_user_id = manager['tg_user_id']

        username_display = f'@{username}' if username else 'Юзернейм не указан'
        tgbot_status = f'🟢 ID в боте {tg_user_id}' if tg_user_id else '🔴 Не зашёл в бота'

        answer += (
            f'{manager_id} \n'
            f'{name} \n'
            f'{username_display} \n'
        )
        if username:
            answer += f'{tgbot_status} \n'
        answer += f'\n'

    if managers:
        answer += 'Присылайте ID (цифру) менеджера чтобы управлять'

    keyboard = kb(
        '+',
        '< назад'
    )

    await bot.send_message(user_id, answer, reply_markup=keyboard)
    set_state(user_id)


async def managers_add_input(bot, user_id):
    answer = (
        'Введите имя нового менеджера (которое будет парситься из писем и документов) \n'
    )
    await bot.send_message(user_id, answer, reply_markup=kb('< назад'))
    set_state(user_id)


async def managers_add_save(bot, user_id, text):
    conn = db.get_conn()
    if not text:
        await bot.send_message(user_id, 'Некорректный ввод')
        return 
    with conn:
        conn.execute(
            'INSERT INTO managers (manager_name) VALUES (?)',
            (text, )
        )
    
    (manager_id, ) = conn.execute('SELECT last_insert_rowid() FROM managers').fetchone()

    set_select_id(user_id, manager_id)

    await manager_menu(bot, user_id)


async def manager_menu(bot, user_id, manager_id=None):
    conn = db.get_conn()
    if manager_id:
        manager = conn.execute(
            'SELECT * FROM managers WHERE id = ?',
            (manager_id, )
        ).fetchone()
        if not manager:
            await bot.send_message(user_id, 'Некорректный ввод')
            return 
        
    else:
        manager_id = get_select_id(user_id)
        manager = conn.execute(
            'SELECT * FROM managers WHERE id = ?',
            (manager_id, )
        ).fetchone()
    
    username = manager['tg_username']
    tg_user_id = manager['tg_user_id']
    username_display = f'@{username}' if username else 'Юзернейм не указан'
    tgbot_status = f'🟢 ID в боте {tg_user_id}' if tg_user_id else '🔴 Не зашёл в бота'

    answer = (
        f'Выбран менеджер ID {manager["id"]} \n\n'
        f'Имя для документов: <code>{manager["manager_name"]}</code> \n\n'
        f'Юзернейм: {username_display} \n\n'
        f'{tgbot_status} \n\n'
    ) 

    keyboard = kb(
        '✏️ Имя',
        '✏️ Юзернейм',
        '❌ Удалить',
        '< назад',
    )
    
    await bot.send_message(user_id, answer, reply_markup=keyboard)
    set_state(user_id)


async def manager_name_input(bot, user_id):
    conn = db.get_conn()
    manager_id = get_select_id(user_id)
    manager = conn.execute('SELECT * FROM managers WHERE id = ?', (manager_id, )).fetchone()
    name = manager['manager_name']

    answer = f'Введите новое имя для менеджера {name}, чтобы переименовать:'
    await bot.send_message(user_id, answer, reply_markup=kb('< назад'))
    set_state(user_id)


async def manager_name_save(bot, user_id, text):
    conn = db.get_conn()
    manager_id = get_select_id(user_id)
    with conn:
        conn.execute(
            'UPDATE managers SET manager_name = ? WHERE id = ?',
            (text, manager_id)
        )
    await bot.send_message(user_id, 'OK')
    await manager_menu(bot, user_id)


async def manager_username_input(bot, user_id):
    conn = db.get_conn()
    manager_id = get_select_id(user_id)
    manager = conn.execute('SELECT * FROM managers WHERE id = ?', (manager_id, )).fetchone()
    if manager['tg_user_id']:
        error_text = 'Нельзя изменить юзернейм пользователя который уже зашёл в бота'
        await bot.send_message(user_id, error_text)
        return 

    answer = 'Юзернейм менеджера: '
    await bot.send_message(user_id, answer, reply_markup=kb('< назад'))
    set_state(user_id)


async def manager_username_save(bot, user_id, text):
    conn = db.get_conn()
    manager_id = get_select_id(user_id)
    manager = conn.execute('SELECT * FROM managers WHERE id = ?', (manager_id, )).fetchone()
    if manager['tg_user_id']:
        error_text = 'Нельзя изменить юзернейм менеджера который уже зашёл в бота'
        await bot.send_message(user_id, error_text)
        return 

    if '/' in text:
        await bot.send_message(user_id, 'Некорректный ввод')
        return 
    
    username = text.replace('@', '')

    with conn:
        conn.execute(
            'UPDATE managers SET tg_username = ? WHERE id = ?',
            (username, manager_id)
        )

    user = conn.execute(
        'SELECT * FROM users WHERE username = ?',
        (username, )
    ).fetchone()
    if user:
        with conn:
            conn.execute(
                "UPDATE managers SET tg_user_id = ? WHERE id = ?",
                (user["tg_user_id"], manager_id)
            )
        manager_name = manager['manager_name']
        await bot.send_message(user["tg_user_id"], f'Вы зарегистрированы как {manager_name}')

    await bot.send_message(user_id, 'OK')
    await manager_menu(bot, user_id)


async def manager_delete_confirm(bot, user_id):
    answer = 'Удалить менеджера?'
    keyboard = kb('Да', '< назад')
    await bot.send_message(user_id, answer, reply_markup=keyboard)
    set_state(user_id)


async def manager_delete(bot, user_id, text):
    if not text == 'Да':
        return 
    
    conn = db.get_conn()
    manager_id = get_select_id(user_id)

    with conn:
        conn.execute(
            'DELETE FROM managers WHERE id = ?',
            (manager_id, )
        )
    
    await bot.send_message(user_id, 'OK')
    await managers_menu(bot, user_id)