import asyncio
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

from tgbot.admin.admins import set_state, get_select_id, set_select_id
from tgbot.admin.utils import kb, send_long_message
import config
import db 


conn = db.get_conn()


async def main_menu(bot, user_id):
    (new_requests_count, ) = conn.execute(
        """
        SELECT COUNT(*) 
        FROM tg_users 
        WHERE manager_name IS NULL 
        AND organization_name IS NOT NULL
        AND is_request_declined = 0
        """
    ).fetchone()
    
    answer = 'Здравствуйте! \n\n'
    if new_requests_count:
        answer += f'🟢 Новых запросов: {new_requests_count}'

    keyboard = kb(
        'Посмотреть запросы',
        'Управление менеджерами',
        #'Разное',
        row_size=1
    )

    await bot.send_message(user_id, answer, reply_markup=keyboard)
    set_state(user_id)


async def see_request(bot, user_id):
    new_user = conn.execute(
        """
        SELECT * 
        FROM tg_users 
        WHERE manager_name IS NULL 
        AND organization_name IS NOT NULL
        AND is_request_declined = 0
        LIMIT 1
        """
    ).fetchone()
    if not new_user:
        await bot.send_message(user_id, 'Нет новых запросов')
        await asyncio.sleep(0.3)
        await main_menu(bot, user_id)
        return 

    organization_name = new_user['organization_name']
    new_user_id = new_user['user_id']
    first_name = new_user['first_name']
    last_name = new_user['last_name']
    name = f'{first_name} {last_name}' if last_name else first_name
    clickable_name = f'<a href="tg://user?id={new_user_id}">{name}</a>'
    username = f'@{new_user["username"]}' if new_user['username'] else 'нет'

    answer = (
        f'Запрос от: {clickable_name} \n'
        f'Юзернейм: {username}\n'
        f'Название организации: {organization_name} \n'
        f'\n'
        f'Введите имя менеджера для этого пользователя:'
    )
    keyboard = kb('❌ Отклонить', '< назад')

    await bot.send_message(user_id, answer, reply_markup=keyboard)
    set_select_id(user_id, new_user_id)
    set_state(user_id)


async def decline_request(bot, user_id):
    new_user_id = get_select_id(user_id)
    with conn:
        conn.execute(
            """
            UPDATE tg_users 
            SET is_request_declined = 1
            WHERE user_id = ?
            """, (new_user_id, )
        )
    await see_request(bot, user_id)


async def process_request(bot, user_id, manager_name):
    new_user_id = get_select_id(user_id)
    with conn:
        conn.execute(
            """
            UPDATE tg_users 
            SET manager_name = ?
            WHERE user_id = ?
            """, (manager_name, new_user_id)
        )
    await bot.send_message(user_id, 'OK')
    await see_request(bot, user_id)



async def managers_menu(bot, user_id):
    managers = conn.execute(
        'SELECT * FROM tg_users WHERE manager_name IS NOT NULL'
    ).fetchall()

    answer = f'- Управление менеджерами - \n\n'
    for manager in managers:
        manager_user_id = manager['user_id']
        first_name = manager['first_name']
        last_name = manager['last_name']
        name = f'{first_name} {last_name}' if last_name else first_name
        clickable_name = f'<a href="tg://user?id={manager_user_id}">{name}</a>'
        username = f'@{manager["username"]}' if manager['username'] else ''
        manager_name = manager['manager_name']
        answer += (
            f'Telegram ID: <code>{manager_user_id}</code>\n'
            f'Telegram: {clickable_name} {username} \n'
            f'Имя менеджера: <code>{manager_name}</code> \n'
            f'\n'
        )
    
    if managers:
        answer += 'Присылайте Telegram ID менеджера, чтобы управлять \n\n'

    keyboard = kb('Отклонённые заявки', '< назад')
    await send_long_message(bot, user_id, answer, reply_markup=keyboard)
    set_state(user_id)


async def declined_requests_menu(bot, user_id):
    declined_requests = conn.execute(
        'SELECT * FROM tg_users WHERE is_request_declined = 1'
    ).fetchall()
    if not declined_requests:
        await bot.send_message(user_id, 'Нет отклонённых заявок')
        return 

    answer = f'- Отклонённые заявки - \n\n'
    for manager in declined_requests:
        manager_user_id = manager['user_id']
        first_name = manager['first_name']
        last_name = manager['last_name']
        name = f'{first_name} {last_name}' if last_name else first_name
        clickable_name = f'<a href="tg://user?id={manager_user_id}">{name}</a>'
        username = f'@{manager["username"]}' if manager['username'] else ''
        answer += (
            f'ID Telegram: <code>{manager_user_id}</code>\n'
            f'Telegram: {clickable_name} {username} \n'
            f'\n'
        )
    
    answer += 'Присылайте Telegram ID пользователя чтобы управлять \n\n'

    keyboard = kb('< назад')
    await send_long_message(bot, user_id, answer, reply_markup=keyboard)
    set_state(user_id)


async def manager_menu(bot, user_id, manager_user_id=None):
    if manager_user_id:
        manager = conn.execute(
            'SELECT * FROM tg_users WHERE user_id = ?',
            (manager_user_id, )
        ).fetchone()
        if not manager:
            await bot.send_message(user_id, 'Incorrect Input')
            return 
        set_select_id(user_id, manager_user_id)
    else:
        manager_user_id = get_select_id(user_id)
        manager = conn.execute(
            'SELECT * FROM tg_users WHERE user_id = ?',
            (manager_user_id, )
        ).fetchone()
    
    manager_user_id = manager['user_id']
    first_name = manager['first_name']
    last_name = manager['last_name']
    name = f'{first_name} {last_name}' if last_name else first_name
    clickable_name = f'<a href="tg://user?id={manager_user_id}">{name}</a>'
    username = f'@{manager["username"]}' if manager['username'] else 'нет'
    manager_name = manager['manager_name']
    if manager_name:
        manager_display = f'Имя менеджера для документов: <code>{manager_name}</code>'
    else:
        manager_display = f'Установите имя менеджера, чтобы открыть доступ'

    answer = (
        f'Выбран пользователь Telegram ID <code>{manager_user_id}</code> \n\n'
        f'{clickable_name} \n'
        f'Юзернейм: {username}\n'
        f'\n'
        f'{manager_display}'
    )
    keyboard = kb(
        '✏️ Имя менеджера',
        '❌ Закрыть доступ',
        '< назад',
    )
    await bot.send_message(user_id, answer, reply_markup=keyboard)
    set_state(user_id)


async def manager_name_input(bot, user_id):
    await bot.send_message(user_id, 'Новое имя менеджера:', reply_markup=kb('< назад'))
    set_state(user_id)


async def manager_name_save(bot, user_id, manager_name):
    manager_user_id = get_select_id(user_id)
    with conn:
        conn.execute(
            """
            UPDATE tg_users SET 
                manager_name = ?,
                is_request_declined = 0
            WHERE user_id = ?
            """, (manager_name, manager_user_id)
        )
    await bot.send_message(user_id, 'OK')
    await manager_menu(bot, user_id)


async def manager_remove_access_confirmation(bot, user_id):
    await bot.send_message(user_id, 'Закрыть доступ?', reply_markup=kb('Да', '< назад'))
    set_state(user_id)


async def manager_remove_access(bot, user_id):
    manager_user_id = get_select_id(user_id)
    with conn:
        conn.execute(
            """
            UPDATE tg_users SET 
                manager_name = NULL,
                is_request_declined = 1
            WHERE user_id = ?
            """, (manager_user_id, )
        )
    await bot.send_message(user_id, 'OK')
    await managers_menu(bot, user_id)


