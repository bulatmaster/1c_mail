import requests

import config 


def report(message=None):
    DEFAULT_MESSAGE = 'Ошибка в 1c_mail'

    if message:
        message = f'1c_mail: {message}'
    else:
        message = DEFAULT_MESSAGE
    

    token = config.EMERGENCY_BOT_TOKEN
    for chat_id in config.ADMIN_IDS:
        url = f'https://api.telegram.org/bot{token}/'   
        requests.get(url + 'sendMessage', params = {
            'chat_id': chat_id,
            'text': message
        })