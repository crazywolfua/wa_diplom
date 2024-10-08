# water_intake_calculator.py
from aiogram.fsm.context import FSMContext
from aiogram import types
from datetime import datetime, timedelta

async def calculate_water_intake(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    gender = user_data.get('gender')
    age = user_data.get('age')
    weight = user_data.get('weight')
    activity = user_data.get('activity')
    climate = user_data.get('climate')
    pregnancy = user_data.get('pregnancy')
    lactation = user_data.get('lactation')
    trimester = user_data.get('trimester')

    base_intake = weight * 30  # Базовая норма воды в миллилитрах (30 мл на кг веса)

    gender_coefficient = 1.1 if gender == 'gender_male' else 1.0

    age_coefficient = 1.0
    if age is not None:
        if age < 4:
            age_coefficient = 1.3  # Дети до 4 лет
        elif 4 <= age < 14:
            age_coefficient = 1.25  # Дети 4-14 лет
        elif 14 <= age < 18:
            age_coefficient = 1.2  # Подростки 14-18 лет
        elif 18 <= age < 30:
            age_coefficient = 1.1  # Молодые взрослые 18-30 лет
        elif 30 <= age < 55:
            age_coefficient = 1.0  # Взрослые 30-55 лет
        elif age >= 55:
            age_coefficient = 0.9  # Пожилые люди старше 55 лет

    activity_coefficient = {
        'activity_low': 1.0,
        'activity_moderate': 1.2,
        'activity_high': 1.3
    }.get(activity, 1.0)

    climate_coefficient = {
        'climate_moderate': 1.0,
        'climate_hot': 1.2,
        'climate_very_hot': 1.3
    }.get(climate, 1.0)

    pregnancy_coefficient = 1.0
    if pregnancy == 'pregnancy_yes':
        if trimester == 'trimester_1':
            pregnancy_coefficient = 1.2
        elif trimester == 'trimester_2':
            pregnancy_coefficient = 1.25
        elif trimester == 'trimester_3':
            pregnancy_coefficient = 1.3

    lactation_coefficient = 1.0
    if lactation:
        lactation_coefficient = 1.5

    water_intake_total = int((base_intake * gender_coefficient * age_coefficient * activity_coefficient *
                          climate_coefficient * pregnancy_coefficient * lactation_coefficient))

    await state.update_data(water_intake_total=water_intake_total)


async def calculate_single_intake(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    water_intake_total = user_data.get('water_intake_total')
    wake_up_time = user_data.get('wake_up_time')
    sleep_time = user_data.get('sleep_time')
    water_interval = int(user_data.get('water_interval'))

    wake_up_time = datetime.combine(datetime.today(), wake_up_time)
    sleep_time = datetime.combine(datetime.today(), sleep_time)

    # Если время сна наступает на следующий день
    if sleep_time <= wake_up_time:
        sleep_time += timedelta(days=1)

    waking_hours = ((sleep_time - wake_up_time).total_seconds() / 3600) - 1  # Время бодрствования в часах
    intervals = waking_hours * (60 / water_interval)
    single_intake = int(water_intake_total / intervals)

    await state.update_data(single_intake=single_intake)