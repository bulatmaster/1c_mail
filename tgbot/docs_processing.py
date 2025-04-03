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
    subject = message['message_subject']
    
    receiver_user_id = None
    error = ''

    # Проверка на наличие файла 
    if not message_files:
        error += 'В письме нет PDF-вложений;\n'

    # Поиск менеджера по имени в теме письма
    managers = {name: id for (id, name) in conn.execute(
        'SELECT id, manager_name FROM managers'
    )}
    manager_id = None
    for name in managers:
        if name in subject:
            manager_id = managers[name]
            break 
    if not manager_id:
        error += 'Не найден менеджер;\n'

    if manager_id:
        manager = conn.execute(
            'SELECT * FROM managers WHERE id = ?',
            (manager_id, )
        ).fetchone()
        if not manager['tg_username']:
            error += 'Не указан юзернейм менеджера;\n'
        if not manager['tg_user_id']:
            error += 'Менеджер не зашёл в бота;\n'
    
        receiver_user_id = manager['tg_user_id']

    if error:
        caption = (
            f'Сообщение не переслано \n'
            f'Тема: {subject} \n'
            f'Дата письма: {message["message_date"]}\n'
            f'Ошибка:\n '
            f'{error}'
        )
        receiver_user_id = config.REPORTS_CHAT_ID

    else:
        caption = message['message_subject']
    
    try:
        for file in message_files:
            file_path = file['filepath']
            await bot.send_document(receiver_user_id, FSInputFile(file_path), caption=caption)
    
    except Exception as e:
        sending_error = f'{e.__class__.__name__}: {e}'
        await emergency.report(f'Ошибка при пересылке документа: {sending_error}')
        return

    rowid = message['rowid']
    success = 1 if not error else 0
    with conn:
        conn.execute(
            """
            UPDATE email_messages SET
                is_processed = 1,
                processed_timestamp = CURRENT_TIMESTAMP,
                success = ?,
                error = ?
            WHERE rowid = ?
            """, (success, error, rowid)
        )

    

async def handle_unsuccess(bot: Bot, message: sqlite3.Row, error: str):
    subject = message['message_subject']
    emergency.report(
        f'Не удалось отправить документ из письма с темой: {subject}. \n'
        f'Ошибка: {error}'
    )