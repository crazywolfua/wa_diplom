# user_states.py
import json
import logging
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.db_user import db_get_user, db_update_user, db_insert_user
from config import redis_client, REDIS_TTL, DATABASE_URL
from converter.datetime_converter import DateTimeConverter
from database.db_utils import DatabaseManager

class UserInfoStates(StatesGroup):
    gender = State()
    birth_date = State()
    age = State()
    weight = State()
    activity = State()
    climate = State()
    wake_up_time = State()
    sleep_time = State()
    water_interval = State()
    pregnancy = State()
    trimester = State()
    lactation = State()
    location = State()
    manual_timezone = State()
    save_result = State()

class UserStateManager:
    def __init__(self, state: FSMContext, user_id: int):
        self.state = state
        self.user_id = user_id
        self.redis_key = f"user_data:{user_id}"


    async def _fetch_user_data_from_fsm(self):
        """Получить данные пользователя из FSM."""
        return await self.state.get_data()


    async def _fetch_user_data_from_db(self, db_pool):
        """Получить данные пользователя из базы данных."""
        return await db_get_user(db_pool, self.user_id)


    async def _fetch_user_data_from_redis(self):
        """Получить данные пользователя из Redis"""
        cached_user_data = await redis_client.get(self.redis_key)
        if cached_user_data:
            cached_user_data = json.loads(cached_user_data)
            return cached_user_data
        return None


    async def _fetch_user_data_from_redis_for_db(self):
        """Получить данные пользователя из Redis и конвертировать даты из строк обратно в объекты datetime."""
        cached_user_data = await redis_client.get(self.redis_key)
        if cached_user_data:
            cached_user_data = json.loads(cached_user_data)
            return DateTimeConverter.convert_string_to_datetime(cached_user_data)
        return None


    async def _save_data_to_redis(self, user_data):
        """Сохранить данные пользователя в Redis с конвертацией дат в строки."""
        user_data = DateTimeConverter.convert_datetime_to_string(user_data)
        await redis_client.set(self.redis_key, json.dumps(user_data), ex=REDIS_TTL)


    async def _compare_and_update_user_data(self, db_user_data, message, db_pool):
        """
        Сравнивает данные из БД с данными из Telegram. Если данные отличаются, обновляет их в БД и сохраняет в Redis.
        """
        telegram_user = message.from_user
        fsm_data = await self._fetch_user_data_from_fsm()
        changes = {}

        for key in ['first_name', 'last_name', 'username', 'language_code', 'is_premium']:
            fsm_value = fsm_data.get(key)
            db_value = db_user_data.get(key)
            telegram_value = getattr(telegram_user, key, None)

            if fsm_value is not None and fsm_value != db_value:
                changes[key] = fsm_value
            elif telegram_value is not None and telegram_value != db_value:
                changes[key] = telegram_value

        if changes:
            logging.info(f"Обновление данных пользователя {self.user_id}: {changes}")
            await db_update_user(db_pool, self.user_id, changes)

        combined_data = {**db_user_data, **changes}
        await self._save_data_to_redis(combined_data)


    async def update_user_data_in_redis(self, user_data: dict):
        """
        Обновляет данные пользователя в Redis только в случае, если произошли изменения.
        """
        cached_user_data = await self._fetch_user_data_from_redis()

        if cached_user_data:
            if user_data != cached_user_data:
                cached_user_data.update(user_data)
                logging.info(f"Обновление данных пользователя {self.user_id} в Redis.")
                await self._save_data_to_redis(cached_user_data)
            else:
                logging.info(f"Данные пользователя {self.user_id} не изменились, обновление кэша не требуется.")
        else:
            logging.info(f"Создание новой записи пользователя {self.user_id} в Redis.")
            await self._save_data_to_redis(user_data)


    async def update_user_data_from_message(self, message):
        """
        Заполняет данные нового пользователя и сохраняет в FSM-сессии.
        """
        user = message.from_user
        user_data = {
            'telegram_id': user.id,
            'chat_id': message.chat.id,
            'is_bot': user.is_bot,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'username': user.username,
            'language_code': user.language_code,
            'is_premium': getattr(user, 'is_premium', False),
        }
        await self.state.update_data(user_data)


    async def ensure_user_data_loaded(self, message, db_pool):
        """
        Проверяет наличие данных о пользователе в Redis. Если данных нет, проверяет наличие в БД.
        Если пользователя нет в БД, инициирует процесс регистрации в FSM.
        """
        cached_user_data = await self._fetch_user_data_from_redis()

        if cached_user_data:
            logging.info(f"Пользователь {self.user_id} найден в Redis. Обновляем TTL.")
            await redis_client.expire(self.redis_key, REDIS_TTL)
            return True

        logging.info(f"Пользователь {self.user_id} не найден в Redis. Проверка в базе данных.")
        existing_user_data = await self._fetch_user_data_from_db(db_pool)

        if existing_user_data:
            logging.info(f"Пользователь {self.user_id} найден в базе данных. Проверка на актуальность данных.")
            await self._compare_and_update_user_data(existing_user_data, message, db_pool)
            return True
        else:
            logging.warning(f"Пользователь {self.user_id} не найден в базе данных. Запуск процесса сбора данных.")
            await self.update_user_data_from_message(message)
            return False


    async def save_user_data_to_redis(self):
        """
        Сохраняет или обновляет данные пользователя в Redis на основе данных из FSM и очищает FSM.
        """
        user_data = await self._fetch_user_data_from_fsm()
        if not user_data:
            logging.error("Нет данных в FSM для сохранения в Redis.")
            return False

        await self._save_data_to_redis(user_data)
        await self.state.clear()
        return True


    async def add_new_user_to_db(self, message):
        """Добавить нового пользователя в базу данных на основе данных из Redis."""
        db_manager = DatabaseManager(DATABASE_URL)
        await db_manager.create_pool()
        db_pool = db_manager.pool
        user_data = await self._fetch_user_data_from_redis_for_db()
        if user_data:
            await db_insert_user(db_pool, user_data)
            existing_user_data = await self._fetch_user_data_from_db(db_pool)
            if existing_user_data:
                await self._compare_and_update_user_data(existing_user_data, message, db_pool)


    async def get_user_data_from_cache(self):
        """Получить данные пользователя из Redis"""
        return await self._fetch_user_data_from_redis()


    async def delete_user_data_from_redis(self):
        """
        Удаляет ключ с данными пользователя из Redis.
        """
        try:
            deleted = await redis_client.delete(self.redis_key)
            if deleted:
                logging.info(f"Данные пользователя {self.user_id} успешно удалены из Redis.")
            else:
                logging.warning(f"Не удалось найти ключ для пользователя {self.user_id} в Redis.")
        except Exception as e:
            logging.error(f"Ошибка при удалении данных пользователя {self.user_id} из Redis: {e}")
