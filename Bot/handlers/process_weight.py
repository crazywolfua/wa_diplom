# process_weight.py
from aiogram.fsm.context import FSMContext
from locales.localization import Localization
from aiogram import types
from handlers.user_states import UserInfoStates
from handlers.user_state_next_previous import transition_to_next_state, handle_back_button, get_user_data

localization = Localization()

async def request_weight(message: types.Message, state: FSMContext):
    await transition_to_next_state(
        message, state, UserInfoStates.weight,
        'weight_prompt', ['back_button']
    )


async def process_weight(message: types.Message, state: FSMContext):
    from handlers.process_pregnancy import request_pregnancy, request_trimester
    from handlers.process_birth_date import request_birth_date
    from handlers.process_activity import request_activity
    user_language = message.from_user.language_code
    trimester_status = await get_user_data(state, 'trimester')
    lactation_status = await get_user_data(state, 'lactation')
    pregnancy_status = await get_user_data(state, 'pregnancy')

    if trimester_status and await handle_back_button(message, state, request_trimester, user_language,
                                                     state_keys_to_reset=['trimester']):
        return
    elif lactation_status and await handle_back_button(message, state, request_pregnancy, user_language,
                                                       state_keys_to_reset=['pregnancy', 'lactation', 'trimester']):
        return
    elif pregnancy_status is not None and await handle_back_button(message, state, request_pregnancy, user_language,
                                                       state_keys_to_reset=['pregnancy', 'lactation', 'trimester']):
        return
    elif await handle_back_button(message, state, request_birth_date, user_language, state_keys_to_reset=['birth_date']):
        return

    try:
        weight = int(message.text)
        if weight < 15 or weight > 350:
            raise ValueError
    except ValueError:
        invalid_weight = await localization.get_translation('invalid_weight', user_language)
        await message.answer(invalid_weight, parse_mode="HTML")
        return

    await state.update_data(weight=weight)
    await request_activity(message, state)