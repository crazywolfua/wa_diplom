# process_wake_up_sleep_time.py
from aiogram.fsm.context import FSMContext
from locales.localization import Localization
from aiogram import types
from datetime import datetime
from handlers.user_state_next_previous import transition_to_next_state, handle_back_button, get_user_data
from handlers.user_states import UserInfoStates

localization = Localization()

async def request_wake_up_time(message: types.Message, state: FSMContext):
    await transition_to_next_state(
        message, state, UserInfoStates.wake_up_time,
        'wake_up_time_prompt', ['back_button']
    )


async def process_wake_up_time(message: types.Message, state: FSMContext):
    from handlers.process_climate import request_climate
    user_language = message.from_user.language_code

    if await handle_back_button(message, state, request_climate, user_language, state_keys_to_reset=['climate']):
        return

    try:
        wake_up_time = datetime.strptime(message.text, "%H:%M").time()
    except ValueError:
        invalid_time_format = await localization.get_translation('invalid_time_format', user_language)
        await message.answer(invalid_time_format, parse_mode="HTML")
        return

    await state.update_data(wake_up_time=wake_up_time)
    await request_sleep_time(message, state)


async def request_sleep_time(message: types.Message, state: FSMContext):
    await transition_to_next_state(
        message, state, UserInfoStates.sleep_time,
        'sleep_time_prompt', ['back_button']
    )


async def process_sleep_time(message: types.Message, state: FSMContext):
    from handlers.process_user_timezone import request_location
    user_language = message.from_user.language_code

    if await handle_back_button(message, state, request_wake_up_time, user_language, state_keys_to_reset=['wake_up_time']):
        return

    try:
        sleep_time = datetime.strptime(message.text, "%H:%M").time()
    except ValueError:
        invalid_time_format = await localization.get_translation('invalid_time_format', user_language)
        await message.answer(invalid_time_format, parse_mode="HTML")
        return

    wake_up_time = await get_user_data(state, 'wake_up_time')
    if wake_up_time >= sleep_time:
        invalid_sleep_time = await localization.get_translation('invalid_sleep_time', user_language)
        await message.answer(invalid_sleep_time, parse_mode="HTML")
        return

    await state.update_data(sleep_time=sleep_time)
    await request_location(message, state)