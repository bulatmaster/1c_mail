from os import getenv
import dotenv

dotenv.load_dotenv()



IMAP_SERVER = getenv('IMAP_SERVER')
IMAP_PORT = getenv('IMAP_PORT')
EMAIL_ACCOUNT = getenv('EMAIL_ACCOUNT')
EMAIL_PASSWORD = getenv('EMAIL_PASSWORD')

EMAIL_FROM = getenv('FROM_EMAIL')


BOT_TOKEN = getenv('BOT_TOKEN')
ADMIN_IDS = [int(user_id) for user_id in getenv('ADMIN_IDS').split(',')]

EMERGENCY_BOT_TOKEN = getenv('EMERGENCY_BOT_TOKEN')

REPORTS_CHAT_ID = getenv('REPORTS_CHAT_ID')

db_path = 'data/database.db'