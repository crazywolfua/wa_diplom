# process_gender.py
from aiogram.fsm.context import FSMContext
from locales.localization import Localization
from aiogram import types
from datetime import datetime
from handlers.user_states import UserInfoStates
from handlers.user_state_next_previous import transition_to_next_state, handle_back_button, get_user_data

localization = Localization()

async def request_birth_date(message: types.Message, state: FSMContext):
    await transition_to_next_state(
        message, state, UserInfoStates.birth_date,
        'age_prompt', ['back_button']
    )


async def process_birth_date(message: types.Message, state: FSMContext):
    from handlers.process_gender import request_gender
    if await handle_back_button(message, state, request_gender, state_keys_to_reset=['gender']):
        return

    try:
        birth_date = datetime.strptime(message.text, "%d.%m.%Y")
        if birth_date < datetime(1900, 1, 1) or birth_date > datetime.now():
            raise ValueError
    except ValueError:
        user_language = message.from_user.language_code
        invalid_age = await localization.get_translation('invalid_age', user_language)
        await message.answer(invalid_age, parse_mode="HTML")
        return

    age = datetime.now().year - birth_date.year
    await state.update_data(birth_date=message.text, age=age)

    # Присваиваем значение None, так как у мужчины не будет этих запросов, а в БД нам что-то записать нужно
    await state.update_data(pregnancy=None, lactation=None, trimester=None)

    gender = await get_user_data(state, 'gender')
    if gender == 'gender_female' and age >= 18:
        from handlers.process_pregnancy import request_pregnancy
        await request_pregnancy(message, state)
    else:
        from handlers.process_weight import request_weight
        await request_weight(message, state)