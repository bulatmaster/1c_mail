import asyncio 
import sqlite3
import logging

from aiogram import Bot 
from aiogram.types import FSInputFile

import config 
import db
import emergency


conn = db.get_conn()


async def main(bot: Bot):
    while True:
        try:
            await check_messages(bot)
            await asyncio.sleep(60)
        except Exception as e:
            emergency.report(f'tgbot.email_parser: {e.__class__.__name__}: {e}')
            logging.exception(e)
            await asyncio.sleep(60)
    

async def check_messages(bot: Bot):
    new_messages = conn.execute(
        'SELECT * FROM email_messages WHERE is_processed = 0'
    ).fetchall()
    for message in new_messages:
        await process_message(bot, message)
    

async def process_message(bot: Bot, message: sqlite3.Row):
    (success, reason) = filter_message(message)
    if not success:
        await report_unsuccess(bot, message, reason=reason)
    
    managers = get_managers(message)
    if not managers:
        await report_unsuccess(bot, message, reason='Не найден менеджер')
    
    for manager in managers:
        (success, reason) = await send_documents(bot, message, manager)
        if success:
            await report_success(bot, message, manager)
        else:
            await report_unsuccess(bot, message, manager=manager, reason=reason)
    
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


def filter_message(message: sqlite3.Row):
    success = True
    reason = ''
    
    rowid = message['rowid']
    docs = conn.execute(
        'SELECT * FROM email_files WHERE message_rowid = ? LIMIT 1',
        (rowid, )
    ).fetchone()
    if not docs:
        success = False 
        reason += 'Нет pdf вложений; \n' 
    
    

    return (success, reason)


def get_managers(message: sqlite3.Row):
    subject = message['message_subject']
    managers = conn.execute(
        """
        SELECT * 
        FROM tg_users
        WHERE manager_name IS NOT NULL
        AND INSTR(?, manager_name) > 0
        """, (subject, )
    ).fetchall()
    return managers 


async def send_documents(bot: Bot, message: sqlite3.Row, manager: sqlite3.Row):
    success = True
    reason = ''

    manager_user_id = manager['user_id']
    message_rowid = message['rowid']
    message_files = conn.execute(
        'SELECT * FROM email_files WHERE message_rowid = ?',
        (message_rowid, )
    ).fetchall()
    caption = message['message_subject']

    for file in message_files:
        file_path = file['file_path']
        try:
            await bot.send_document(manager_user_id, FSInputFile(file_path), caption=caption)
        except Exception as e:
            reason = f'{e.__class__.__name__}: {e}'
            return (False, reason)

    return (success, reason)


async def report_unsuccess(bot: Bot, message: sqlite3.Row = None,
                           manager: sqlite3.Row = None, reason: str = None,
                           is_error: bool = True):
    sign = '❗️' if is_error else ''

    report = (
        f'{sign} Письмо не переслано \n'
        f'Тема: {message["message_subject"]} \n'
        f'Дата: {message["message_date"]} \n'
        f'От: {message["from_account"]} \n'
        f'uid письма: {message["message_uid"]} \n'
        f'Внутренний rowid письма: {message["rowid"]} \n'
        f'Причина: {reason} \n'
    )
    await bot.send_message(config.REPORTS_CHAT_ID, report, parse_mode=None)
    
    files = conn.execute(
        'SELECT * FROM email_files WHERE message_rowid = ?', 
        (message['rowid'], )
    ).fetchall()
    for file in files:
        file_path = file['file_path']
        caption = message['message_subject']
        try:
            await bot.send_document(
                config.REPORTS_CHAT_ID, 
                FSInputFile(file_path), 
                caption=caption
            )
        except Exception as e:
            await bot.send_message(config.REPORTS_CHAT_ID, (
                f'Ошибка при отправке документа {file_path} '
                f'(письмо {message["message_subject"]}): {e.__class__.__name__}: {e}'
            ), parse_mode=None)
        

async def report_success(bot: Bot, message: sqlite3.Row, manager: sqlite3.Row):
    manager_name = manager['manager_name']
    if manager['last_name']:
        tg_name = f'{manager["first_name"]} {manager["last_name"]}'
    else:
        tg_name = manager['first_name']
    if manager['username']:
        tg_name += f' (@{manager["username"]})'
    
    report = (
        f'✅ Письмо переслано \n'
        f'Тема: {message["message_subject"]} \n'
        f'Менеджер: {manager_name} \n'
        f'{tg_name} \n'
    )

    await bot.send_message(config.REPORTS_CHAT_ID, report, parse_mode=None)