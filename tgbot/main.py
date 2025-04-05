import asyncio
import logging 
import sys 

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import ErrorEvent, Message

import config 
import emergency
from tgbot.admin.disp import admin_disp
from tgbot.user.disp import user_disp
from tgbot.email_parser import email_parser



logging_level = logging.DEBUG if 'debug' in sys.argv else logging.INFO
logging.basicConfig(
    level=logging_level,
    format='%(name)s : %(asctime)s : %(threadName)s : [%(levelname)s] : %(message)s',
    handlers=[
        logging.StreamHandler()
    ],
)


async def errors_handler(event: ErrorEvent):
    emergency.report(f'{event.exception.__class__.__name__}: {event.exception}\n(update {event.update.update_id})')
    raise 


async def messages_handler(message: Message, bot: Bot):
    if message.chat.type != 'private':
        return
    
    user_id = message.from_user.id
    text = message.text

    if user_id in config.ADMIN_IDS:
        await admin_disp(message)
    else:
        await user_disp(message)
        return 


async def main():
    bot = Bot(
        token=config.BOT_TOKEN, 
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    dp.message.register(messages_handler)
    dp.errors.register(errors_handler)

    asyncio.create_task(email_parser.main(bot))

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())