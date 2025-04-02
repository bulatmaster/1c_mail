
from aiogram import Bot 
from aiogram.types import Message 

from tgbot import user_handlers as u
from tgbot import admin_handlers as h
from tgbot import admin_back_button
from tgbot.admin_utils import get_state
import config 


async def messages_handler(message: Message, bot: Bot):
    if message.chat.type != 'private':
        return
    user_id = message.from_user.id
    text = message.text

    u.register_or_update_user(message.from_user)

    if user_id not in config.ADMIN_IDS:
        await u.cmd_start(message)
        return 

    if text == '/start':
        await h.main_menu(bot, user_id)
        return 
    
    state = get_state(user_id)

    if text == '< назад':
        await admin_back_button.back_button_handler(bot, user_id, state)
        return 
    
    match state:
        case 'main_menu':
            match text:
                case '👤 Менеджеры':
                    await h.managers_menu(bot, user_id)
        case 'managers_menu':
            match text:
                case '+':
                    await h.managers_add_input(bot, user_id)
                case _:
                    await h.manager_menu(bot, user_id, manager_id=text)
        case 'managers_add_input':
            await h.managers_add_save(bot, user_id, text)
        case 'manager_menu':
            match text:
                case '✏️ Имя':
                    await h.manager_name_input(bot, user_id)
                case '✏️ Юзернейм':
                    await h.manager_username_input(bot, user_id)
                case '❌ Удалить':
                    await h.manager_delete_confirm(bot, user_id)
        case 'manager_name_input':
            await h.manager_name_save(bot, user_id, text)
        case 'manager_username_input':
            await h.manager_username_save(bot, user_id, text)
        case 'manager_delete_confirm':
            await h.manager_delete(bot, user_id, text)


