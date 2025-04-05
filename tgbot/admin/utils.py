import sqlite3 
import inspect 

from aiogram import Bot 
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup

import db 


async def send_long_message(
        bot: Bot,
        chat_id: int,
        text: str,
        reply_markup=None,  
        **kwargs
) -> None:
    """Для отправки длинных текстовых сообщений (админбот) - разбивает по частям"""

    def split_text_by_newline(text, max_length=3000):
        parts = []
        while len(text) > max_length:
            # Найти последний перенос строки \n в пределах max_length
            split_index = text.rfind('\n', 0, max_length)
            
            if split_index == -1:  # Если переноса строки нет в пределах max_length
                split_index = max_length  # Разделить ровно на max_length символов
            
            # Добавить часть текста в список
            parts.append(text[:split_index].strip())
            # Удалить добавленную часть из текста
            text = text[split_index:].lstrip()
        
        # Добавить оставшийся текст
        if text:
            parts.append(text.strip())
        
        return parts
    
    parts = split_text_by_newline(text)
    for part in parts:
        await bot.send_message(
            chat_id=chat_id,
            text=part,
            reply_markup=reply_markup,
            **kwargs
        )



def kb(*buttons: str, row_size=2) -> ReplyKeyboardMarkup:
    """
    Генерирует клавиатуру с кнопками.
    
    :param buttons: Произвольное количество текстов кнопок
    :return: Объект ReplyKeyboardMarkup с заданными параметрами
    """
    builder = ReplyKeyboardBuilder()

    for button_text in buttons:
        builder.button(text=button_text)
    
    # Можно добавить логику для автонастройки количества кнопок в строке
    builder.adjust(row_size)  # Настраиваем количество кнопок в строке

    # Создаем и возвращаем клавиатуру с нужными параметрами
    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=False,
    )

