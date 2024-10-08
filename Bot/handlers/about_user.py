# about_user.py
from locales.localization import Localization
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from handlers.user_states import UserStateManager

async def about_user(message: types.Message, state: FSMContext, db_pool):
    localization = Localization()
    user_language = message.from_user.language_code
    user_id = message.from_user.id
    user_state_manager = UserStateManager(state, user_id)
    cached_user_data = await user_state_manager.get_user_data_from_cache()

    if not cached_user_data:
        user_data_loaded = await user_state_manager.ensure_user_data_loaded(message, db_pool)
        if user_data_loaded:
            cached_user_data = await user_state_manager.get_user_data_from_cache()
        else:
            user_not_found = await localization.get_translation('cache_user_not_found', user_language)
            await message.answer(user_not_found)
            return

    keys_for_translated = [
        'about_user_first_name', 'about_user_last_name', 'about_user_gender',
        'about_user_birth_date', 'about_user_pregnancy', 'about_user_lactation',
        'about_user_trimester', 'about_user_age', 'about_user_weight',
        'about_user_activity', 'about_user_climate', 'about_user_timezone',
        'about_user_wake_up_time', 'about_user_sleep_time', 'about_user_water_interval',
        'about_user_water_intake_total', 'about_user_single_intake', 'about_user_created_at',
        'about_user_updated_at', 'about_user_water_updated_at'
    ]

    translated_keys = await localization.get_translations(keys_for_translated, user_language)

    cache_message = ''

    fields_for_user = [
        'first_name', 'last_name', 'gender', 'birth_date', 'pregnancy', 'lactation', 'trimester', 'age', 'weight',
        'activity', 'climate', 'timezone', 'wake_up_time', 'sleep_time', 'water_interval', 'water_intake_total',
        'single_intake', 'created_at', 'updated_at', 'water_updated_at'
    ]

    fields_for_translated = ['gender', 'activity', 'climate', 'pregnancy', 'lactation', 'trimester']

    for key in fields_for_user:
        value = cached_user_data.get(key)
        if value is not None:
            field_name_key = f"about_user_{key}"
            field_name = translated_keys[field_name_key]
            if key in fields_for_translated:
                value_translation = await localization.get_translation(value, user_language)
                cache_message += f"{field_name} {value_translation}\n"
            else:
                cache_message += f"{field_name} {value}\n"
    await message.answer(cache_message)


def get_about_user_router(db_pool):
    router = Router()

    @router.message(Command('about_user'))
    async def about_user_handler(message: types.Message, state: FSMContext):
        await about_user(message, state, db_pool)

    return router

