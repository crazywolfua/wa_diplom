# localization.py
import json
import logging
from typing import Dict
from config import redis_client

class Localization:
    def __init__(self, locales_path: str = 'locales', default_language: str = 'en') -> None:
        """
        Инициализация класса Localization.
        Параметры:
        - locales_path: Путь к папке с локализациями (по умолчанию 'locales')
        - default_language: Язык по умолчанию (по умолчанию 'en')
        """
        self.locales_path = locales_path
        self.default_language = default_language

    async def _load_translation_file(self, language: str) -> Dict[str, str]:
        """
        Загружает файл перевода для указанного языка и возвращает его в виде словаря.
        Если файл не существует или возникает ошибка при чтении, возвращает пустой словарь.
        """
        try:
            with open(f'{self.locales_path}/{language}.json', 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            logging.warning(f"Файл перевода для языка {language} не найден.")
            return {}
        except json.JSONDecodeError:
            logging.error(f"Ошибка при чтении JSON для языка {language}.")
            return {}

    async def _get_or_load_translation(self, language: str) -> Dict[str, str]:
        """
        Возвращает словарь с переводами для указанного языка.
        Если переводы есть в Redis, они возвращаются из Redis.
        Если переводов в Redis нет, загружаются из файла, кэшируются в Redis и возвращаются.
        """
        # Пробуем получить переводы из Redis
        cached_translations = await redis_client.get(f'translations:{language}')
        if cached_translations:
            return json.loads(cached_translations)

        # Если переводов нет в кэше, загружаем их из файла
        translations = await self._load_translation_file(language)

        # Кэшируем в Redis
        await redis_client.set(f'translations:{language}', json.dumps(translations), ex=3600)

        return translations

    async def get_translation(self, key: str, language: str) -> str:
        """
        Получение перевода по ключу для указанного языка.
        Если перевод не найден для переданного языка, возвращается перевод на языке по умолчанию.
        Если ключ не найден ни в одном языке, возвращается сам ключ.
        """
        translations = await self._get_or_load_translation(language)
        if key in translations:
            return translations[key]

        # Если ключ не найден в указанном языке, ищем перевод на языке по умолчанию
        default_translations = await self._get_or_load_translation(self.default_language)
        return default_translations.get(key, key)


    async def get_translations(self, keys: list, language: str) -> Dict[str, str]:
        """
        Получение переводов для списка ключей для указанного языка.
        Если перевод не найден для переданного языка, возвращается перевод на языке по умолчанию.
        Если ключ не найден ни в одном языке, возвращается сам ключ в словаре.
        """
        translations = await self._get_or_load_translation(language)
        default_translations = await self._get_or_load_translation(self.default_language)

        result = {}
        for key in keys:
            result[key] = translations.get(key, default_translations.get(key, key))

        return result
