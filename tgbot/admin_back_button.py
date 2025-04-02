from aiogram import Bot

from tgbot import admin_handlers as h


async def back_button_handler(bot: Bot, user_id, state):
    match state:
        case 'managers_menu':
            await h.main_menu(bot, user_id)
        case 'managers_add_input':
            await h.managers_menu(bot, user_id)
        case 'manager_menu':
            await h.managers_menu(bot, user_id)
        case 'manager_name_input':
            await h.manager_menu(bot, user_id)
        case 'manager_username_input':
            await h.manager_menu(bot, user_id)
        case 'manager_delete_confirm':
            await h.manager_menu(bot, user_id)