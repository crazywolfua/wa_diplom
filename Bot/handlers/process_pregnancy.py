# process_pregnancy.py
from aiogram.fsm.context import FSMContext
from locales.localization import Localization
from aiogram import types
from handlers.user_states import UserInfoStates
from handlers.user_state_next_previous import transition_to_next_state, handle_back_button
from handlers.process_birth_date import request_birth_date
from handlers.process_weight import request_weight

localization = Localization()

async def request_pregnancy(message: types.Message, state: FSMContext):
    await transition_to_next_state(
        message, state, UserInfoStates.pregnancy,
        'pregnancy_prompt', ['pregnancy_no', 'pregnancy_yes', 'lactation', 'back_button']
    )


async def process_pregnancy(message: types.Message, state: FSMContext):
    user_language = message.from_user.language_code

    if await handle_back_button(message, state, request_birth_date, user_language, state_keys_to_reset=['birth_date', 'age']):
        return

    keys_for_translated = ['pregnancy_yes', 'pregnancy_no', 'lactation']
    translated_keys_tmp = await localization.get_translations(keys_for_translated, user_language)
    translated_keys = {value: key for key, value in translated_keys_tmp.items()}

    if message.text in translated_keys:
        if translated_keys[message.text] == 'pregnancy_yes':
            await state.update_data(pregnancy='pregnancy_yes')
            await request_trimester(message, state)
        elif translated_keys[message.text] == 'pregnancy_no':
            await state.update_data(pregnancy='pregnancy_no')
            await request_weight(message, state)
        elif translated_keys[message.text] == 'lactation':
            await state.update_data(lactation='lactation')
            await request_weight(message, state)
    else:
        invalid_value = await localization.get_translation('invalid_value', user_language)
        await message.answer(invalid_value, parse_mode="HTML")
        return


async def request_trimester(message: types.Message, state: FSMContext):
    await transition_to_next_state(
        message, state, UserInfoStates.trimester,
        'trimester_prompt', ['trimester_1', 'trimester_2', 'trimester_3', 'back_button'],
        rows=2
    )


async def process_trimester(message: types.Message, state: FSMContext):
    user_language = message.from_user.language_code

    if await handle_back_button(message, state, request_pregnancy, user_language, state_keys_to_reset=['pregnancy', 'lactation']):
        return

    keys_for_translated = ['trimester_1', 'trimester_2', 'trimester_3']
    translated_keys_tmp = await localization.get_translations(keys_for_translated, user_language)
    translated_keys = {value: key for key, value in translated_keys_tmp.items()}

    if message.text in translated_keys:
        await state.update_data(trimester=translated_keys[message.text])
        await request_weight(message, state)
    else:
        invalid_value = await localization.get_translation('invalid_value', user_language)
        await message.answer(invalid_value, parse_mode="HTML")

        return