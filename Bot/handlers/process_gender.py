# process_gender.py
from aiogram.fsm.context import FSMContext
from locales.localization import Localization
from aiogram import types
from handlers.user_states import UserInfoStates
from handlers.user_state_next_previous import transition_to_next_state, handle_back_button
from aiogram.types import ReplyKeyboardRemove

localization = Localization()

async def request_gender(message: types.Message, state: FSMContext):
    await transition_to_next_state(
        message, state, UserInfoStates.gender,
        'gender_prompt', ['gender_male', 'gender_female', 'back_button'], rows=2
    )

async def process_gender(message: types.Message, state: FSMContext):
    user_language = message.from_user.language_code

    keys_for_translated = ['gender_male', 'gender_female', 'back_button']
    translated_keys_tmp = await localization.get_translations(keys_for_translated, user_language)
    translated_keys = {value: key for key, value in translated_keys_tmp.items()}

    if message.text in translated_keys:
        if translated_keys[message.text] == 'back_button':
            await message.answer('⬅️', reply_markup=ReplyKeyboardRemove())
            await state.clear()
            return
        elif translated_keys[message.text] == 'gender_male' or translated_keys[message.text] == 'gender_female':
            await state.update_data(gender=translated_keys[message.text])
    else:
        gender_invalid = await localization.get_translation('gender_invalid', user_language)
        await message.answer(gender_invalid, parse_mode="HTML")
        return

    from handlers.process_birth_date import request_birth_date
    await request_birth_date(message, state)