# db_utils.py

import asyncpg
import logging


class DatabaseManager:
    def __init__(self, db_url):
        self.db_url = db_url
        self.pool = None

    async def create_pool(self):
        """Создание пула подключений к PostgreSQL"""
        logging.info("Создание пула подключений к базе данных...")
        self.pool = await asyncpg.create_pool(self.db_url)

    async def _check_table_exists(self, connection, table_name):
        """Проверка существования таблицы"""
        result = await connection.fetchval(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name=$1);", table_name
        )
        return result

    async def _check_column_exists(self, connection, table_name, column_name):
        """Проверка существования колонки в таблице"""
        result = await connection.fetchval(
            '''
            SELECT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name=$1 AND column_name=$2
            );
            ''', table_name, column_name
        )
        return result

    async def _ensure_columns_exist(self, connection, table_name, columns):
        """Проверка и добавление недостающих колонок"""
        for column_name, column_definition in columns.items():
            exists = await self._check_column_exists(connection, table_name, column_name)
            if not exists:
                await connection.execute(f'ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition};')
                logging.info(f"Добавлена колонка {column_name} в таблицу {table_name}.")

    async def create_or_update_table_users(self, connection):
        """Создание или обновление таблицы users"""
        table_name = 'users'

        # Проверка существования таблицы
        table_exists = await self._check_table_exists(connection, table_name)
        if not table_exists:
            await connection.execute('''
                CREATE TABLE users (
                    telegram_id BIGINT UNIQUE NOT NULL PRIMARY KEY,
                    chat_id BIGINT UNIQUE NOT NULL,
                    is_bot BOOLEAN NOT NULL DEFAULT FALSE,
                    first_name VARCHAR(65),
                    last_name VARCHAR(65),
                    username VARCHAR(35),
                    language_code VARCHAR(10),
                    is_premium BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                    gender VARCHAR(20),
                    birth_date DATE,
                    age INTEGER,
                    weight INTEGER,
                    activity VARCHAR(20),
                    climate VARCHAR(20),
                    timezone VARCHAR(50),
                    wake_up_time TIME,
                    sleep_time TIME,
                    water_interval INTEGER,
                    pregnancy VARCHAR(20),
                    lactation VARCHAR(20),
                    trimester VARCHAR(20), 
                    end_day BOOLEAN DEFAULT FALSE,
                    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
                );
            ''')
            logging.info(f"Таблица {table_name} создана.")
        else:
            logging.info(f"Таблица {table_name} уже существует. Проверяем наличие всех колонок...")
            columns_to_check = {
                'telegram_id': 'BIGINT UNIQUE NOT NULL PRIMARY KEY',
                'chat_id': 'BIGINT UNIQUE NOT NULL',
                'is_bot': 'BOOLEAN NOT NULL DEFAULT FALSE',
                'first_name': 'VARCHAR(65)',
                'last_name': 'VARCHAR(65)',
                'username': 'VARCHAR(35)',
                'language_code': 'VARCHAR(10)',
                'is_premium': 'BOOLEAN DEFAULT FALSE',
                'created_at': 'TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP',
                'gender': 'VARCHAR(20)',
                'birth_date': 'DATE',
                'age': 'INTEGER',
                'weight': 'INTEGER',
                'activity': 'VARCHAR(20)',
                'climate': 'VARCHAR(20)',
                'timezone': 'VARCHAR(50)',
                'wake_up_time': 'TIME',
                'sleep_time': 'TIME',
                'water_interval': 'INTEGER',
                'pregnancy': 'VARCHAR(20)',
                'lactation': 'VARCHAR(20)',
                'trimester': 'VARCHAR(20)',
                'end_day': 'BOOLEAN DEFAULT FALSE',
                'updated_at': 'TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP'
            }
            await self._ensure_columns_exist(connection, table_name, columns_to_check)

    async def create_or_update_table_users_daily(self, connection):
        """Создание или обновление таблицы users_daily"""
        table_name = 'users_daily_water'

        # Проверка существования таблицы
        table_exists = await self._check_table_exists(connection, table_name)
        if not table_exists:
            await connection.execute('''
                CREATE TABLE users_daily_water (
                    user_id BIGINT REFERENCES users(telegram_id) ON DELETE CASCADE,
                    water_intake_total INTEGER,
                    single_intake INTEGER,
                    water_drank_today INTEGER DEFAULT 0,
                    water_updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id)
                );
            ''')
            logging.info(f"Таблица {table_name} создана.")
        else:
            logging.info(f"Таблица {table_name} уже существует. Проверяем наличие всех колонок...")
            columns_to_check = {
                'water_intake_total': 'INTEGER',
                'single_intake': 'INTEGER',
                'water_drank_today': 'INTEGER DEFAULT 0',
                'water_updated_at': 'TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP'
            }
            await self._ensure_columns_exist(connection, table_name, columns_to_check)

    async def check_and_create_tables(self):
        """Проверка и создание таблиц, если они не существуют"""
        async with self.pool.acquire() as connection:
            await self.create_or_update_table_users(connection)
            await self.create_or_update_table_users_daily(connection)
