from aiogram import Bot

from tgbot.admin import handlers as h
from tgbot.admin.admins import get_select_id
import db 


conn = db.get_conn()


async def back_button_handler(bot: Bot, user_id, state):
    match state:
        case 'see_request':
            await h.main_menu(bot, user_id)
        case 'managers_menu':
            await h.main_menu(bot, user_id)
        case 'declined_requests_menu':
            await h.managers_menu(bot, user_id)
        case 'manager_menu':
            selected_user_id = get_select_id
            selected_user = conn.execute(
                'SELECT * FROM tg_users WHERE user_id = ?', 
                (selected_user_id, )
            ).fetchone()
            if selected_user['manager_name']:
                await h.managers_menu(bot, user_id)
            else:
                await h.declined_requests_menu(bot, user_id)
        case 'manager_name_input':
            await h.manager_menu(bot, user_id)
        case 'manager_delete_confirmation':
            await h.manager_menu(bot, user_id)
        case _:
            await h.main_menu(bot, user_id)