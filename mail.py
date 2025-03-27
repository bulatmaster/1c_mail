import imaplib
import email
from email.header import decode_header
import os
import config

def clean(text):
    # Удаляет странные символы из заголовков
    return ''.join(c if c.isalnum() or c in "._- " else '_' for c in text)

def decode_mime_words(s):
    decoded = decode_header(s)
    return ''.join(
        str(part[0], part[1] or 'utf-8') if isinstance(part[0], bytes) else str(part[0])
        for part in decoded
    )

def save_pdf_attachments(msg, save_folder):
    for part in msg.walk():
        content_type = part.get_content_type()
        content_disposition = str(part.get("Content-Disposition") or "")
        if 'attachment' in content_disposition or 'inline' in content_disposition:
            if content_type == 'application/pdf':
                filename = part.get_filename()
                if filename:
                    filename = decode_mime_words(filename)
                    filename = clean(filename)
                else:
                    filename = "attachment.pdf"

                filepath = os.path.join(save_folder, filename)
                with open(filepath, "wb") as f:
                    f.write(part.get_payload(decode=True))
                print(f"✅ PDF сохранён: {filepath}")

def check_inbox():
    mail = imaplib.IMAP4_SSL(config.IMAP_SERVER, config.IMAP_PORT)
    mail.login(config.EMAIL_ACCOUNT, config.EMAIL_PASSWORD)

    mail.select("inbox")
    status, messages = mail.search(None, f'(FROM "{config.FROM_EMAIL}")')
    if status != "OK":
        print("Не удалось получить письма")
        return

    message_ids = messages[0].split()
    print(f"Найдено писем: {len(message_ids)}")

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

        print(f"\n--- Письмо ---")
        print(f"От: {from_}")
        print(f"Тема: {subject}")
        print(f"Дата: {date_}")
        print(f"UID письма: {uid}")

        # Скачиваем PDF-вложения
        save_pdf_attachments(msg, "pdfs")

    mail.logout()

if __name__ == "__main__":
    os.makedirs("pdfs", exist_ok=True)  # Создаёт папку pdfs, если её нет
    check_inbox()
