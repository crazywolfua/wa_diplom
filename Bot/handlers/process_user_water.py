# process_user_water.py
from aiogram.fsm.context import FSMContext
from locales.localization import Localization
from aiogram import types
from handlers.user_states import UserInfoStates
from handlers.user_state_next_previous import transition_to_next_state, handle_back_button

localization = Localization()

async def request_water_interval(message: types.Message, state: FSMContext):
    await transition_to_next_state(
        message, state, UserInfoStates.water_interval,'interval_prompt',
        ['interval_15', 'interval_30', 'interval_45', 'interval_60', 'back_button'], rows=2
    )


async def process_water_interval(message: types.Message, state: FSMContext):
    from handlers.process_user_timezone import request_location

    if await handle_back_button(message, state, request_location, state_keys_to_reset=['timezone']):
        return

    user_language = message.from_user.language_code
    water_interval = ['15', '30', '45', '60']

    if message.text in water_interval:
        await state.update_data(water_interval=int(message.text))
        await process_water_intake_calculator(message, state)
    else:
        invalid_value = await localization.get_translation('invalid_value', user_language)
        await message.answer(invalid_value, parse_mode="HTML")
        return


async def process_water_intake_calculator(message: types.Message, state: FSMContext):
    from handlers.water_intake_calculator import calculate_water_intake, calculate_single_intake

    await calculate_water_intake(message, state)
    await calculate_single_intake(message, state)

    user_data = await state.get_data()
    user_language = user_data.get('language_code')
    name = user_data.get('first_name')
    water_intake = user_data.get('water_intake_total')
    interval = user_data.get('water_interval')
    single_intake = user_data.get('single_intake')

    water_message_template = await localization.get_translation('calculation_complete', user_language)
    water_message = water_message_template.format(name=name, water_intake=water_intake, interval=interval, single_intake=single_intake)
    await message.answer(water_message, parse_mode="HTML")

    from handlers.user_info import request_save_user
    await request_save_user(message, state)