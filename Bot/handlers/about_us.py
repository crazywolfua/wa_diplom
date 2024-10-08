# about_us.py
from locales.localization import Localization
from aiogram import Router, types
from aiogram.filters import Command

async def about_us_command(message: types.Message):
    localization = Localization()
    user_language = message.from_user.language_code
    about_us = await localization.get_translation('about_us', user_language)
    await message.answer(about_us, parse_mode="HTML")


def get_about_us_router():
    router = Router()

    @router.message(Command('about_us'))
    async def about_us_handler(message: types.Message):
        await about_us_command(message)

    return router