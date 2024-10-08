# start.py
import logging
from aiogram import types, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from locales.localization import Localization
from handlers.user_states import UserStateManager
from handlers.user_keyboard import create_keyboard
from aiogram.fsm.state import State, StatesGroup
from handlers.bot_menu import set_user_bot_commands
from handlers.delete_me import delete_me_command
from handlers.about_us import about_us_command
from handlers.feedback import feedback
from handlers.help_user import help_user
from handlers.about_user import about_user
from handlers.process_gender import request_gender

localization = Localization()

class StartStates(StatesGroup):
    waiting_for_start_button = State()

def get_start_router(db_pool):
    router = Router()

    @router.message(Command("start"))
    async def start_handler(message: Message, state: FSMContext):
        """Обработка команды /start"""
        user = message.from_user
        logging.info(f"Получена команда /start от пользователя {user.id}")
        user_state_manager = UserStateManager(state, user.id)
        user_data_loaded = await user_state_manager.ensure_user_data_loaded(message, db_pool)
        await set_user_bot_commands(message.bot, message)

        if user_data_loaded:
            cached_user_data = await user_state_manager.get_user_data_from_cache()
            last_visit = cached_user_data['updated_at']
            await send_welcome_back_message(message, user, 'welcome_back', user.language_code, last_visit)
        else:
            logging.info(f"Пользователь {user.id} не найден в базе данных, начат сбор данных.")
            await send_welcome_message(message, user, 'welcome_message', state)

    async def send_welcome_message(message: types.Message, user: types.User, welcome_key: str, state: FSMContext):
        user_language = user.language_code
        welcome_message_template = await localization.get_translation(welcome_key, user_language)
        welcome_message = welcome_message_template.format(name=user.first_name)
        button_prompt = await localization.get_translation('start_button_prompt', user_language)
        full_message = f"{welcome_message}\n\n{button_prompt}"
        keyboard = await create_keyboard(user_language, 'start_button')

        await message.answer(full_message, reply_markup=keyboard, parse_mode="HTML")
        await state.set_state(StartStates.waiting_for_start_button)

    async def send_welcome_back_message(message: types.Message, user: types.User, welcome_key: str,
                                      user_language: str, last_visit):

        welcome_back_message_template = await localization.get_translation(welcome_key, user_language)
        welcome_back_message = welcome_back_message_template.format(name=user.first_name, last_visit=last_visit)

        await message.answer(welcome_back_message, parse_mode="HTML")

    @router.message(StartStates.waiting_for_start_button)
    async def start_button_handler(message: types.Message, state: FSMContext):
        """Обрабатываем нажатие кнопки start_button и команд меню"""
        user_language = message.from_user.language_code
        start_button_text = await localization.get_translation('start_button', user_language)
        '''Принудительно устанавливаем ключ start_button так как бот мультиязычный'''
        text_command = message.text
        if text_command == start_button_text:
            text_command = 'start_button'

        message_mapping = {
            'start_button': lambda: request_gender(message, state),
            '/about_user': lambda: about_user(message, state, db_pool),
            '/help': lambda: help_user(message),
            '/about_us': lambda: about_us_command(message),
            '/feedback': lambda: feedback(message),
            '/delete_me': lambda: delete_me_command(message, state, db_pool)
        }
        if text_command in message_mapping:
            await message_mapping[text_command]()
        else:
            invalid_start = await localization.get_translation('invalid_start', user_language)
            await message.answer(invalid_start, parse_mode="HTML")

    return router
