import sqlite3 

from aiogram import Bot
from aiogram.types import FSInputFile

import config 
import db 


conn = db.get_conn()


async def report_failed(bot: Bot, message: sqlite3.Row = None,
                           manager: sqlite3.Row = None, reason: str = None):
    report = (
        f'❗️ Ошибка при пересылке \n'
        f'\n'
        f'От: {message["from_account"]} \n'
        f'Тема: {message["message_subject"]} \n'
        f'\n'
        f'Ошибка: {reason} \n'
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
        f'✅ Переслано письмо '
        f'"{message["message_subject"]}"'
        f'менеджеру {manager_name}'
    )

    await bot.send_message(config.REPORTS_CHAT_ID, report, parse_mode=None)


async def report_filter_not_passed(bot, message, reason):
    report = (
        f'ℹ️ Письмо не прошло фильтр \n'
        f'\n'
        f'От: {message["from_account"]} \n'
        f'Тема: {message["message_subject"]} \n'
        f'\n'
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