# db_user.py
from datetime import datetime
import asyncpg
import logging
import pytz


async def db_insert_user(db_pool, user_data: dict):
    """
    Добавляет нового пользователя в БД
    :param db_pool: Пул соединений с базой данных
    :param user_data: Данные пользователя для вставки
    """
    current_time_utc = datetime.now(pytz.UTC)

    user_columns = [
        'telegram_id', 'chat_id', 'is_bot', 'first_name', 'last_name', 'username', 'language_code',
        'is_premium', 'created_at', 'gender', 'birth_date', 'age', 'weight', 'activity',
        'climate', 'timezone', 'wake_up_time', 'sleep_time', 'water_interval', 'pregnancy',
        'lactation', 'trimester', 'end_day', 'updated_at'
    ]

    user_values = [
        user_data.get('telegram_id'),
        user_data.get('chat_id'),
        user_data.get('is_bot', False),
        user_data.get('first_name'),
        user_data.get('last_name'),
        user_data.get('username'),
        user_data.get('language_code'),
        user_data.get('is_premium', False),
        current_time_utc,
        user_data.get('gender'),
        user_data.get('birth_date'),
        user_data.get('age'),
        user_data.get('weight'),
        user_data.get('activity'),
        user_data.get('climate'),
        user_data.get('timezone'),
        user_data.get('wake_up_time'),
        user_data.get('sleep_time'),
        user_data.get('water_interval'),
        user_data.get('pregnancy'),
        user_data.get('lactation'),
        user_data.get('trimester'),
        False,
        current_time_utc
    ]

    user_placeholders = ", ".join([f"${i + 1}" for i in range(len(user_columns))])
    user_columns_str = ", ".join(user_columns)

    user_query = f"INSERT INTO users ({user_columns_str}) VALUES ({user_placeholders})"

    daily_columns = ['user_id', 'water_intake_total', 'single_intake', 'water_updated_at']
    daily_values = [
        user_data['telegram_id'],
        user_data.get('water_intake_total'),
        user_data.get('single_intake'),
        current_time_utc
    ]

    daily_placeholders = ", ".join([f"${i + 1}" for i in range(len(daily_values))])
    daily_columns_str = ", ".join(daily_columns)

    daily_query = f"INSERT INTO users_daily_water ({daily_columns_str}) VALUES ({daily_placeholders})"

    try:
        async with db_pool.acquire() as connection:
            async with connection.transaction():
                await connection.execute(user_query, *user_values)
                await connection.execute(daily_query, *daily_values)

        logging.info(
            f"Новый пользователь с id={user_data['telegram_id']} успешно добавлен в базы данных (users и users_daily_water).")
    except asyncpg.PostgresError as e:
        logging.error(f"Ошибка при добавлении нового пользователя {user_data['telegram_id']}: {e}")
        raise

async def db_update_user(db_pool, user_id: int, changes: dict):
    """
    Обновляет данные пользователя в БД

    :param db_pool: Пул соединений с базой данных
    :param user_id: Идентификатор пользователя
    :param changes: Словарь с обновляемыми данными
    """
    if not changes:
        logging.info("Нет изменений для обновления.")
        return

    set_clause = ", ".join([f"{key} = ${idx}" for idx, key in enumerate(changes.keys(), start=1)])
    query = f"UPDATE users SET {set_clause} WHERE telegram_id = ${len(changes) + 1}"

    try:
        async with db_pool.acquire() as connection:
            await connection.execute(query, *changes.values(), user_id)
        logging.info(f"Данные пользователя с id={user_id} успешно обновлены в базе данных.")
    except asyncpg.PostgresError as e:
        logging.error(f"Ошибка при обновлении данных пользователя {user_id}: {e}")
        raise


async def db_get_user(pool: asyncpg.pool.Pool, telegram_id: int):
    """Получение данных пользователя из таблиц `users` и `users_daily_water`"""
    async with pool.acquire() as connection:
        logging.info(f"Запрос данных пользователя {telegram_id} из баз данных (users и users_daily_water).")

        query = '''
            SELECT u.*, ud.water_intake_total, ud.single_intake, ud.water_updated_at
            FROM users u
            LEFT JOIN users_daily_water ud ON u.telegram_id = ud.user_id
            WHERE u.telegram_id = $1;
        '''

        return await connection.fetchrow(query, telegram_id)


async def db_delete_user(pool: asyncpg.pool.Pool, telegram_id: int):
    """Удаление данных пользователя из таблицы users и связанных таблиц"""
    async with pool.acquire() as connection:
        logging.info(f"Удаление пользователя {telegram_id} из базы данных.")
        await connection.execute('''
            DELETE FROM users WHERE telegram_id = $1;
        ''', telegram_id)
