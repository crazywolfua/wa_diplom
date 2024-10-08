# bot_menu.py
from aiogram import Bot, types
from aiogram.types import BotCommandScopeChat
from locales.localization import Localization

localization = Localization()

async def set_user_bot_commands(bot: Bot, message: types.Message):
    user_language = message.from_user.language_code
    command_start = await localization.get_translation('command_start', user_language)
    command_about_user = await localization.get_translation('command_about_user', user_language)
    command_help = await localization.get_translation('command_help', user_language)
    command_about_us = await localization.get_translation('command_about_us', user_language)
    command_feedback = await localization.get_translation('command_feedback', user_language)
    command_delete_me = await localization.get_translation('command_delete_me', user_language)

    commands = [
        types.BotCommand(command="/start", description=command_start),
        types.BotCommand(command="/about_user", description=command_about_user),
        types.BotCommand(command="/help", description=command_help),
        types.BotCommand(command="/about_us", description=command_about_us),
        types.BotCommand(command="/feedback", description=command_feedback),
        types.BotCommand(command="/delete_me", description=command_delete_me),
    ]

    await bot.set_my_commands(commands, scope=BotCommandScopeChat(chat_id=message.chat.id))
