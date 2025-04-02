import asyncio
import logging 
import sys 

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import ErrorEvent

from tgbot import disp, docs_processing
import config 
import emergency



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


async def main():
    bot = Bot(
        token=config.BOT_TOKEN, 
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    dp.message.register(disp.messages_handler)
    dp.errors.register(errors_handler)

    asyncio.create_task(docs_processing.main(bot))

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())