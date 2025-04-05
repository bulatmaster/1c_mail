import imaplib
import email
from email.header import decode_header
import os
import time 
import logging 
import sys 
import sqlite3 

import emergency
import config
from email_checker.db import register_message, is_message_processed



logging_level = logging.DEBUG if 'debug' in sys.argv else logging.INFO
logging.basicConfig(
    level=logging_level,
    format='%(name)s : %(asctime)s : %(threadName)s : [%(levelname)s] : %(message)s',
    handlers=[
        logging.StreamHandler()
    ],
)


def main():
    logging.info('- запуск мониторинга почты -')
    while True:
        try:
            check_inbox()
        except Exception as e:
            emergency.report(f'email_checker: {e.__class__.__name__}: {e}')
            logging.exception(e)
        finally:
            time.sleep(300)
    


def check_inbox():
    """
    Проверяет почту 
    """
    mail = imaplib.IMAP4_SSL(config.IMAP_SERVER, config.IMAP_PORT)
    mail.login(config.EMAIL_ACCOUNT, config.EMAIL_PASSWORD)

    mail.select("inbox")
    status, messages = mail.search(None, 'ALL')
    if status != "OK":
        emergency.report('Не удалось получить письма')
        logging.error("Не удалось получить письма")
        return

    message_ids = messages[0].split()
    logging.debug(f"Найдено писем: {len(message_ids)}")

    for num in reversed(message_ids):
        process_message(mail, num)
        time.sleep(1)

    mail.logout()


def process_message(mail, num):
    """
    Обрабатывает письмо
    """
    typ, msg_data = mail.fetch(num, '(RFC822)')
    raw_email = msg_data[0][1]
    msg = email.message_from_bytes(raw_email)
    subject = decode_mime_words(msg.get("Subject", ""))
    from_account = decode_mime_words(msg.get("From", ""))
    message_date = msg.get("Date", "")

    typ, uid_data = mail.fetch(num, '(UID)')
    uid_response = uid_data[0].decode()
    uid = uid_response.split('UID')[1].strip(' )')

    account = config.EMAIL_ACCOUNT

    if is_message_processed(account, uid):
        logging.debug(f'Пропускаю обработанное письмо {uid}')
        return 

    logging.debug(f"От: {from_account}")
    logging.debug(f"Тема: {subject}")
    logging.debug(f"Дата: {message_date}")
    logging.debug(f"UID письма: {uid}")

    # Скачиваем PDF-вложения
    file_paths = save_pdf_attachments(msg, uid)

    register_message(account, from_account, uid, subject, message_date, file_paths)
    logging.info(f'Зарегистрировано новое письмо uid {uid}')

    logging.debug('Помечаю прочитанным')
    mail.store(num, '+FLAGS', '\\Seen')


def save_pdf_attachments(msg, uid) -> list:
    """
    Скачивает все pdf-вложения и возвращает список путей к сохраненным файлам 
    """
    SAVE_FOLDER = 'data/pdfs'
    os.makedirs(SAVE_FOLDER, exist_ok=True)

    file_paths = []

    n = 0
    for part in msg.walk():
        content_type = part.get_content_type()
        content_disposition = str(part.get("Content-Disposition") or "")
        if not ('attachment' in content_disposition or 'inline' in content_disposition):
            continue 
        if not content_type == 'application/pdf':
            continue 
        
        n += 1
        original_filename = part.get_filename()
        original_filename = decode_mime_words(original_filename)
        save_filename = f'{original_filename.split(".pdf")[0]}_{uid}_{n}.pdf'
        save_path = os.path.join(SAVE_FOLDER, save_filename)
        with open(save_path, "wb") as f:
            f.write(part.get_payload(decode=True))
        logging.debug(f"PDF сохранён: {save_path}")
        file_paths.append(save_path)
    
    return file_paths 


def clean(text):
    # Удаляет странные символы из заголовков
    # Нужна, чтобы имена файлов (или заголовки) не содержали 
    # запрещённых/специальных символов и не ломались при сохранении на диск.
    return ''.join(c if c.isalnum() or c in "._- " else '_' for c in text)


def decode_mime_words(s):
    decoded = decode_header(s)
    return ''.join(
        str(part[0], part[1] or 'utf-8') if isinstance(part[0], bytes) else str(part[0])
        for part in decoded
    )


if __name__ == '__main__':
    main()