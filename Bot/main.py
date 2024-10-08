# main.py
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from database.db_utils import DatabaseManager
from handlers import register_routers
from config import API_TOKEN, DATABASE_URL, redis_client


bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


async def on_startup():
    logging.info("Запуск бота...")
    db_manager = DatabaseManager(DATABASE_URL)
    await db_manager.create_pool()
    db_pool = db_manager.pool
    logging.debug("Пул соединений с БД создан.")

    await db_manager.check_and_create_tables()
    logging.info("База данных готова.")

    register_routers(dp, db_pool)
    logging.debug("Хэндлеры зарегистрированы.")


async def on_shutdown():
    logging.info("Бот завершает работу...")

    # Обязательно удалить перед выгрузкой на сервер
    await redis_client.flushdb()
    logging.info("Кэш Redis очищен...")

    await redis_client.aclose()
    logging.info("Redis закрыт...")

    await dp.storage.close()
    logging.info("Диспетчер закрыт...")


async def main():
    try:
        await on_startup()

        try:
            await dp.start_polling(bot)
        finally:
            await on_shutdown()
    except Exception as e:
        logging.error(f"Ошибка при запуске бота: {e}")
        raise

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
