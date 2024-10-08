# precess_activity.py
from aiogram.fsm.context import FSMContext
from locales.localization import Localization
from aiogram import types
from handlers.user_states import UserInfoStates
from handlers.user_state_next_previous import transition_to_next_state, handle_back_button

localization = Localization()

async def request_activity(message: types.Message, state: FSMContext):
    await transition_to_next_state(
        message, state, UserInfoStates.activity,
        'activity_prompt', ['activity_low', 'activity_moderate', 'activity_high', 'back_button']
    )


async def process_activity(message: types.Message, state: FSMContext):
    from handlers.process_weight import request_weight
    from handlers.process_climate import request_climate
    user_language = message.from_user.language_code
    if await handle_back_button(message, state, request_weight, user_language, state_keys_to_reset=['weight']):
        return

    keys_for_translated = ['activity_low', 'activity_moderate', 'activity_high']
    translated_keys_tmp = await localization.get_translations(keys_for_translated, user_language)
    translated_keys = {value: key for key, value in translated_keys_tmp.items()}

    if message.text in translated_keys:
        await state.update_data(activity=translated_keys[message.text])
        await request_climate(message, state)
    else:
        invalid_value = await localization.get_translation('invalid_value', user_language)
        await message.answer(invalid_value, parse_mode="HTML")
        return