# process_climate.py
from aiogram.fsm.context import FSMContext
from locales.localization import Localization
from aiogram import types
from handlers.user_states import UserInfoStates
from handlers.user_state_next_previous import transition_to_next_state, handle_back_button

localization = Localization()

async def request_climate(message: types.Message, state: FSMContext):
    await transition_to_next_state(
        message, state, UserInfoStates.climate,
        'climate_prompt', ['climate_moderate', 'climate_hot', 'climate_very_hot', 'back_button']
    )


async def process_climate(message: types.Message, state: FSMContext):
    from handlers.process_activity import request_activity
    from handlers.process_wake_up_sleep_time import request_wake_up_time
    user_language = message.from_user.language_code

    if await handle_back_button(message, state, request_activity, user_language, state_keys_to_reset=['activity']):
        return

    keys_for_translated = ['climate_moderate', 'climate_hot', 'climate_very_hot']
    translated_keys_tmp = await localization.get_translations(keys_for_translated, user_language)
    translated_keys = {value: key for key, value in translated_keys_tmp.items()}

    if message.text in translated_keys:
        await state.update_data(climate=translated_keys[message.text])
        await request_wake_up_time(message, state)
    else:
        invalid_value = await localization.get_translation('invalid_value', user_language)
        await message.answer(invalid_value, parse_mode="HTML")

        return