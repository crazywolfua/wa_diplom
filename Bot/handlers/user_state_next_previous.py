# user_state_next_previous.py
from aiogram.fsm.context import FSMContext
from aiogram import types
from aiogram.fsm.state import State
from locales.localization import Localization
from handlers.user_keyboard import create_keyboard

localization = Localization()

async def get_user_data(state: FSMContext, key: str):
    user_data = await state.get_data()
    return user_data.get(key)


async def transition_to_next_state(
        message: types.Message, state: FSMContext,
        next_state: State, prompt_key: str,
        keyboard_keys: list, rows=1, custom_buttons=None
):

    user_language = message.from_user.language_code
    prompt = await localization.get_translation(prompt_key, user_language)
    keyboard = await create_keyboard(user_language, *keyboard_keys, custom_buttons=custom_buttons, rows=rows)

    await message.answer(prompt, reply_markup=keyboard, parse_mode="HTML")
    await state.set_state(next_state)


async def handle_back_button(message: types.Message, state: FSMContext, previous_state_function,
                             user_language=None, state_keys_to_reset=None):
    if not user_language:
        user_language = message.from_user.language_code

    if message.text == await localization.get_translation('back_button', user_language):
        if state_keys_to_reset:
            reset_data = {key: None for key in state_keys_to_reset}
            await state.update_data(**reset_data)
        await previous_state_function(message, state)
        return True
    return False