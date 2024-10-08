# user_info.py
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import ContentType
from locales.localization import Localization
from handlers.user_states import UserStateManager, UserInfoStates
from handlers.user_state_next_previous import transition_to_next_state
from handlers.process_gender import process_gender
from handlers.process_birth_date import process_birth_date
from handlers.process_weight import process_weight
from handlers.process_activity import process_activity
from handlers.process_climate import process_climate
from handlers.process_wake_up_sleep_time import process_wake_up_time, process_sleep_time
from handlers.process_user_water import process_water_interval
from handlers.process_pregnancy import process_pregnancy, process_trimester
from handlers.process_user_timezone import process_location, process_manual_timezone
from aiogram.types import ReplyKeyboardRemove

localization = Localization()


async def request_save_user(message: types.Message, state: FSMContext):
    await transition_to_next_state(
        message, state, UserInfoStates.save_result,'save_result_prompt',
        ['save_result', 'back_button'], rows=1
    )



async def process_save_result(message: types.Message, state: FSMContext):
    user_language = message.from_user.language_code
    from handlers.user_state_next_previous import handle_back_button
    from handlers.process_user_water import request_water_interval
    if await handle_back_button(message, state, request_water_interval, user_language,
                                state_keys_to_reset=['water_interval']):
        return

    user_id = message.from_user.id
    user_state_manager = UserStateManager(state, user_id)
    save_result = await localization.get_translation('save_result', user_language)

    if message.text == save_result:
        await user_state_manager.save_user_data_to_redis()
        await user_state_manager.add_new_user_to_db(message)
        successful_save = await localization.get_translation('successful_save', user_language)
        await message.answer(successful_save, reply_markup=ReplyKeyboardRemove(), parse_mode="HTML")
        await state.clear()



def get_user_info_router():
    router = Router()
    state_handlers = {
        UserInfoStates.gender: process_gender,
        UserInfoStates.birth_date: process_birth_date,
        UserInfoStates.weight: process_weight,
        UserInfoStates.activity: process_activity,
        UserInfoStates.climate: process_climate,
        UserInfoStates.wake_up_time: process_wake_up_time,
        UserInfoStates.sleep_time: process_sleep_time,
        UserInfoStates.water_interval: process_water_interval,
        UserInfoStates.pregnancy: process_pregnancy,
        UserInfoStates.trimester: process_trimester,
        UserInfoStates.location: process_location,
        UserInfoStates.manual_timezone: process_manual_timezone,
        UserInfoStates.save_result: process_save_result,
    }

    for state, handler in state_handlers.items():
        if state == UserInfoStates.location:
            router.message.register(handler, state, F.content_type.in_([ContentType.LOCATION, ContentType.TEXT]))
        else:
            router.message(state)(handler)

    return router
