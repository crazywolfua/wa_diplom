# user_keyboard.py
from typing import List
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from locales.localization import Localization

localization = Localization()

async def create_keyboard(user_language: str, *button_keys: str, custom_buttons: List[str] = None,
                          rows: int = None) -> ReplyKeyboardMarkup:
    buttons = []
    keyboard = []
    if custom_buttons:
        buttons = [KeyboardButton(text=btn) for btn in custom_buttons]
        buttons = buttons + [KeyboardButton(text= await localization.get_translation(key, user_language)) for key in button_keys]
    else:
        buttons = [
            KeyboardButton(text=await localization.get_translation(key, user_language), request_location=True)
            if key == 'send_location' else KeyboardButton(text=await localization.get_translation(key, user_language))
            for key in button_keys
        ]

    if rows:
        keyboard = [buttons[i:i + rows] for i in range(0, len(buttons), rows)]
    else:
        keyboard = [buttons]

    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)