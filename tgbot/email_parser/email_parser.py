import asyncio 
import sqlite3
import logging

from aiogram import Bot 
from aiogram.types import FSInputFile

import config 
import db
import emergency
from tgbot.email_parser import reports as r, messages as m


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
    new_messages = m.get_new_messages()
    for message in new_messages:
        await process_message(bot, message)
    

async def process_message(bot: Bot, message: sqlite3.Row):
    (success, reason) = filter_message(message)
    if not success:
        await r.report_filter_not_passed(bot, message, reason=reason)
        m.set_processed(message)
        return 
    
    managers = get_managers(message)
    if not managers:
        await r.report_failed(bot, message, reason='Не найден менеджер')
        m.set_processed(message)
        return 
    
    for manager in managers:
        (success, reason) = await send_documents(bot, message, manager)
        if success:
            await r.report_success(bot, message, manager)
        else:
            await r.report_failed(bot, message, manager=manager, reason=reason)
    
    m.set_processed(message)


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


