import imaplib
import email
from email.header import decode_header
import os
import time 
import logging 
import sys 

from bot import emergency
import config


logging_level = logging.DEBUG if 'debug' in sys.argv else logging.INFO
logging.basicConfig(
    level=logging_level,
    format='%(name)s : %(asctime)s : %(threadName)s : [%(levelname)s] : %(message)s',
    handlers=[
        logging.StreamHandler()
    ],
)



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


def save_pdf_attachments(msg, uid) -> str:
    SAVE_FOLDER = 'data/pdfs'
    os.makedirs(SAVE_FOLDER, exist_ok=True)

    for part in msg.walk():
        content_type = part.get_content_type()
        content_disposition = str(part.get("Content-Disposition") or "")
        if not ('attachment' in content_disposition or 'inline' in content_disposition):
            continue 
        if not content_type == 'application/pdf':
            continue 

        filename = f'{uid}.pdf'

        filepath = os.path.join(SAVE_FOLDER, filename)
        with open(filepath, "wb") as f:
            f.write(part.get_payload(decode=True))
        logging.info(f"PDF сохранён: {filepath}")
        return filepath


def check_inbox():
    mail = imaplib.IMAP4_SSL(config.IMAP_SERVER, config.IMAP_PORT)
    mail.login(config.EMAIL_ACCOUNT, config.EMAIL_PASSWORD)

    mail.select("inbox")
    status, messages = mail.search(None, f'(FROM "{config.FROM_EMAIL}")')
    if status != "OK":
        emergency.report('Не удалось получить письма')
        logging.error("Не удалось получить письма")
        return

    message_ids = messages[0].split()
    logging.debug(f"Найдено писем: {len(message_ids)}")

    for num in reversed(message_ids[-10:]):
        typ, msg_data = mail.fetch(num, '(RFC822)')
        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)

        subject = decode_mime_words(msg.get("Subject", ""))
        from_ = decode_mime_words(msg.get("From", ""))
        date_ = msg.get("Date", "")

        typ, uid_data = mail.fetch(num, '(UID)')
        uid_response = uid_data[0].decode()
        uid = uid_response.split('UID')[1].strip(' )')

        f"От: {from_}"
        f"Тема: {subject}"
        f"Дата: {date_}"
        f"UID письма: {uid}"

        # Скачиваем PDF-вложения
        filepath = save_pdf_attachments(msg, uid)

    mail.logout()


def main():
    logging.info('- запуск -')
    os.makedirs("data/pdfs", exist_ok=True)
    while True:
        check_inbox()
        time.sleep(300)    


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        emergency.report(f'{e.__class__.__name__}: {e}')
        raise 
