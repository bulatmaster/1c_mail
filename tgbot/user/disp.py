from aiogram.types import Message 

from tgbot.user import users
import config 


async def user_disp(message: Message):
    user_id = message.from_user.id
    text = message.text
    bot = message.bot

    is_new_user = users.register_or_update_user(message.from_user)
    user = users.get_user(user_id)

    if is_new_user:
        await message.answer('Здравствуйте! Пожалуйста, напишите название вашей организации')
    
    elif not user['organization_name']:
        users.save_organization_name(user_id, text)
        await message.answer('Спасибо! Ваш запрос в обработке.')
        
        for admin_id in config.ADMIN_IDS:
            await bot.send_message(admin_id, '🟢 Новый запрос \n Смотреть: /start')
        await bot.send_message(config.REPORTS_CHAT_ID, '🟢 Новый запрос в боте')
    
    elif user['is_request_declined']:
        await message.answer(
            'Ваш запрос отклонён. \n'
            'Свяжитесь с вашим менеджером, если произошла ошибка'
        )
    
    elif user['manager_name']:
        manager_name = user['manager_name']
        await message.answer(f'Вы зарегистрированы как {manager_name}')
    
    else:
        await message.answer('Ваш запрос в обработке')