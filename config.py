from os import getenv
import dotenv

dotenv.load_dotenv()



IMAP_SERVER = getenv('IMAP_SERVER')
IMAP_PORT = getenv('IMAP_PORT')
EMAIL_ACCOUNT = getenv('EMAIL_ACCOUNT')
EMAIL_PASSWORD = getenv('EMAIL_PASSWORD')


FROM_EMAIL = getenv('FROM_EMAIL')