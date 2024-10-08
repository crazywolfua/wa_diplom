# help_user.py
from locales.localization import Localization
from aiogram import types

async def help_user(message: types.Message):

    print('Здесь будет помощь пользователю')
    return