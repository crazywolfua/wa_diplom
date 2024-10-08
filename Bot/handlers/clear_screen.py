# clear_screen.py
import logging
from aiogram import types

async def clear_screen(message: types.Message):
    chat_id = message.chat.id
    last_message_id = message.message_id

    for message_id in range(last_message_id, 0, -1):
        try:
            await message.bot.delete_message(chat_id, message_id)
        except Exception as e:
            logging.warning(f"Не удалось удалить сообщение {message_id}: {e}")
            break
