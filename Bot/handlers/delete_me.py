# delete_me.py
import logging
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from database.db_user import db_delete_user, db_get_user
from locales.localization import Localization
from handlers.user_states import UserStateManager
from handlers.user_keyboard import create_keyboard
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove

localization = Localization()

class DeleteStates(StatesGroup):
    waiting_for_press_button = State()


async def delete_me_command(message: types.Message, state: FSMContext, db_pool):
    """Обработка команды /delete_me и вывод предупреждения о возможном удалении данных"""
    user_language = message.from_user.language_code
    user_id = message.from_user.id
    user_data = await db_get_user(db_pool, user_id)

    if user_data:
        delete_warning = await localization.get_translation('delete_warning', user_language)
        keyboard = await create_keyboard(user_language, 'confirm_delete_button', 'cancel_button')

        await message.answer(delete_warning, reply_markup=keyboard, parse_mode="HTML")
        await state.set_state(DeleteStates.waiting_for_press_button)
    else:
        delete_warning = await localization.get_translation('db_user_not_found', user_language)
        await message.answer(delete_warning, parse_mode="HTML")


async def confirm_delete_handler(message: types.Message, state: FSMContext, db_pool):
    """Обработка подтверждения удаления данных"""
    user_id = message.from_user.id
    user_language =message.from_user.language_code
    user_data = await db_get_user(db_pool, user_id)
    # Проверяем наличие юзера в БД
    if user_data:
        await db_delete_user(db_pool, user_id)
    else:
        logging.error(f"Ошибка: User {user_id} отсутствует в БД")
        error_message = await localization.get_translation('delete_error_message', user_language)
        return await message.answer(error_message, parse_mode="HTML")

    farewell_message = await localization.get_translation('farewell_message', user_language)
    await message.answer(farewell_message, reply_markup=ReplyKeyboardRemove(), parse_mode="HTML")

    user_state_manager = UserStateManager(state, user_id)
    await user_state_manager.delete_user_data_from_redis()

    await state.clear()


async def cancel_delete_handler(message: types.Message):
    """Обработка отмены удаления данных"""
    user_language =message.from_user.language_code
    cancel_message = await localization.get_translation('cancel_message', user_language)
    await message.answer(cancel_message, parse_mode="HTML")


def get_delete_me_router(db_pool):
    router = Router()

    @router.message(Command('delete_me'))
    async def delete_me_handler(message: types.Message, state: FSMContext):
        await delete_me_command(message, state, db_pool)


    @router.message(DeleteStates.waiting_for_press_button)
    async def press_button_handler(message: types.Message, state: FSMContext):
        user_language = message.from_user.language_code
        confirm_delete_button = await localization.get_translation('confirm_delete_button', user_language)
        cancel_button = await localization.get_translation('cancel_button', user_language)

        if message.text.strip() == confirm_delete_button:
            await confirm_delete_handler(message, state, db_pool)
        elif message.text.strip() == cancel_button:
            await cancel_delete_handler(message)

    return router
