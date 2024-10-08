# process_user_timezone.py
from aiogram.fsm.context import FSMContext
from locales.localization import Localization
from aiogram import types
from datetime import datetime
from timezonefinder import TimezoneFinder
import pytz
from handlers.user_state_next_previous import transition_to_next_state, handle_back_button
from handlers.user_states import UserInfoStates
from handlers.process_wake_up_sleep_time import request_sleep_time
from handlers.process_user_water import request_water_interval

localization = Localization()

async def request_location(message: types.Message, state: FSMContext):
    await transition_to_next_state(
        message, state, UserInfoStates.location,
        'location_prompt', ['send_location', 'manual_timezone', 'back_button']
    )


async def process_location(message: types.Message, state: FSMContext):
    user_language = message.from_user.language_code

    if await handle_back_button(message, state, request_sleep_time, user_language, state_keys_to_reset=['sleep_time']):
        return

    if message.location:
        lat = message.location.latitude
        lon = message.location.longitude

        tf = TimezoneFinder()
        timezone_str = tf.timezone_at(lat=lat, lng=lon)

        if timezone_str:
            user_timezone = pytz.timezone(timezone_str)
            now = datetime.now(user_timezone)
            utc_offset_timedelta = now.utcoffset()
            total_seconds = int(utc_offset_timedelta.total_seconds())
            hours_offset = total_seconds // 3600
            minutes_offset = abs((total_seconds % 3600) // 60)
            utc_offset_str = f"UTC{'+' if hours_offset >= 0 else '-'}{abs(hours_offset)}:{minutes_offset:02}"
            await state.update_data(timezone=utc_offset_str)

        else:
            await message.answer(await localization.get_translation('invalid_location', user_language), parse_mode="HTML")
            return

        await request_water_interval(message, state)

    elif message.text == await localization.get_translation('manual_timezone', user_language):
        await request_manual_timezone(message, state)


async def request_manual_timezone(message: types.Message, state: FSMContext):
    await transition_to_next_state(
        message, state, UserInfoStates.manual_timezone,
        'manual_timezone_prompt', ['back_button'],
        custom_buttons=[f"UTC{'+' if i >= 0 else ''}{i:02}:00" for i in range(-12, 13)], rows=3
    )


async def process_manual_timezone(message: types.Message, state: FSMContext):
    if await handle_back_button(message, state, request_location, state_keys_to_reset=['timezone']):
        return

    user_language = message.from_user.language_code
    timezone = [f"UTC{'+' if i >= 0 else ''}{i:02}:00" for i in range(-12, 13)]

    if message.text in timezone:
        await state.update_data(timezone=message.text)
        await request_water_interval(message, state)
    else:
        invalid_value = await localization.get_translation('invalid_value', user_language)
        await message.answer(invalid_value, parse_mode="HTML")
        return