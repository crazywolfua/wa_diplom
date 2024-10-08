# config.py
import os
import logging
import redis.asyncio as redis
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv('API_TOKEN')
if not API_TOKEN:
    raise ValueError("API_TOKEN is not set in .env file")

DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in .env file")

LOG_LEVEL = os.getenv('LOG_LEVEL')
if not LOG_LEVEL:
    raise ValueError("LOG_LEVEL is not set in .env file")

LOG_FILE = os.getenv('LOG_FILE')
if not LOG_FILE:
    raise ValueError("LOG_FILE is not set in .env file")

REDIS_URL = os.getenv('REDIS_URL')
if not REDIS_URL:
    raise ValueError("REDIS_URL is not set in .env file")

REDIS_TTL = os.getenv('REDIS_TTL')
if not REDIS_TTL:
    raise ValueError("REDIS_TTL is not set in .env file")

redis_client = redis.from_url(REDIS_URL, decode_responses=True)

log_level_dict = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}

log_level = log_level_dict.get(LOG_LEVEL.upper())
if log_level is None:
    raise ValueError(f"Invalid value LOG_LEVEL: {LOG_LEVEL}")

logger = logging.getLogger()
logger.setLevel(log_level)

file_handler = logging.FileHandler(LOG_FILE)
file_handler.setLevel(log_level)  # Используем общий уровень
file_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))

console_handler = logging.StreamHandler()
console_handler.setLevel(log_level)  # Используем общий уровень
console_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))

logger.addHandler(file_handler)
logger.addHandler(console_handler)

logging.info("Конфигурация загружена успешно.")