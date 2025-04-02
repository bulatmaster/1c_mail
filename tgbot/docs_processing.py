import asyncio 
import sqlite3

from aiogram import Bot 
from aiogram.types import FSInputFile

import config 
import db
import emergency

conn = db.get_conn()


async def main(bot: Bot):
    while True:
        await check_new_docs(bot)
        await asyncio.sleep(60)
    

async def check_new_docs(bot: Bot):
    new_email_messages = conn.execute(
        'SELECT * FROM email_messages WHERE is_processed = 0'
    ).fetchall()
    for message in new_email_messages:
        await process_message(bot, message)
    

async def process_message(bot: Bot, message: sqlite3.Row):
    message_rowid = message['rowid']
    message_files = conn.execute(
        'SELECT * FROM email_files WHERE message_rowid = ?',
        (message_rowid, )
    ).fetchall()

    if not message_files:
        await handle_unsuccess(bot, message, 'Нет вложений в письме')
        return 

    managers = {name: id for (id, name) in conn.execute(
        'SELECT id, manager_name FROM managers'
    )}

    subject = message['message_subject']
    manager_id = None
    for name in managers:
        if name in subject:
            manager_id = managers[name]
            break 
    
    if not manager_id:
        await handle_unsuccess(bot, message, 'Не найден менеджер')
        return 
    
    manager = conn.execute(
        'SELECT * FROM managers WHERE id = ?',
        (manager_id, )
    ).fetchone()
    if not manager['tg_user_id']:
        await handle_unsuccess(bot, message, 'Менеджер не зашёл в бота')
        return 
    
    manager_user_id = manager['tg_user_id']
    caption = message['message_subject']

    try:
        for file in message_files:
            file_path = file['filepath']
            await bot.send_document(manager_user_id, FSInputFile(file_path), caption=caption)
    except Exception as e:
        error = f'{e.__class__.__name__}: {e}'
        await handle_unsuccess(bot, message, error)
        return 

    

async def handle_unsuccess(bot: Bot, message: sqlite3.Row, error: str):
    subject = message['message_subject']
    emergency.report(
        f'Не удалось отправить документ из письма с темой: {subject}. \n'
        f'Ошибка: {error}'
    )