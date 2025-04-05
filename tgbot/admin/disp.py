from aiogram.types import Message

from tgbot.admin import back_button, handlers as h, admins
from tgbot.admin.admins import get_state


async def admin_disp(message: Message):
    text = message.text
    user_id = message.from_user.id
    bot = message.bot

    if text == '/start':
        await h.main_menu(bot, user_id)
        return 
    
    state = get_state(user_id)

    if text == '< назад':
        await back_button.back_button_handler(bot, user_id, state)
        return 
    
    match state:
        case None:
            await h.main_menu(bot, user_id)

        case 'main_menu':
            match text:
                case 'Посмотреть запросы':
                    await h.see_request(bot, user_id)
                case 'Управление менеджерами':
                    await h.managers_menu(bot, user_id)
        
        case 'see_request':
            match text:
                case '❌ Отклонить':
                    await h.decline_request(bot, user_id)
                case _:
                    await h.process_request(bot, user_id, text)
                    
        case 'managers_menu':
            match text:
                case 'Отклонённые заявки':
                    await h.declined_requests_menu(bot, user_id)
                case _:
                    await h.manager_menu(bot, user_id, manager_user_id=text)
        
        case 'declined_requests_menu':
            match text:
                case _:
                    await h.manager_menu(bot, user_id, manager_user_id=text)
        
        case 'manager_menu':
            match text:
                case '✏️ Имя менеджера':
                    await h.manager_name_input(bot, user_id)
                case '❌ Закрыть доступ':
                    await h.manager_remove_access_confirmation(bot, user_id)
        case 'manager_name_input':
            await h.manager_name_save(bot, user_id, text)
        case 'manager_remove_access_confirmation':
            match text:
                case 'Да':
                    await h.manager_remove_access(bot, user_id)
        