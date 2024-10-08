# datetime_converter.py
import logging
from datetime import datetime, time, date, timedelta, timezone


class DateTimeConverter:
    datetime_keys = {'updated_at', 'birth_date', 'created_at'}
    time_keys = {'wake_up_time', 'sleep_time'}

    @staticmethod
    def convert_datetime_to_string(data: dict) -> dict:
        """
        Преобразует все объекты datetime и time в строки в соответствующем формате для хранения в Redis.
        """
        user_timezone = data['timezone']

        for key, value in data.items():
            if key == 'updated_at' or 'created_at' and isinstance(value, datetime):
                # Специальное форматирование для 'updated_at' и 'created_at' в формате 'ГГГГ-ММ-ДД ЧЧ:ММ:СС'
                try:
                    local_user_time = DateTimeConverter.local_user_time(user_timezone, value)
                    data[key] = local_user_time.strftime("%d.%m.%Y %H:%M:%S")
                except ValueError:
                    logging.warning(f"Не удалось преобразовать значение {value} для ключа {key} в строку")
            elif key in DateTimeConverter.datetime_keys and isinstance(value, date):
                # Форматирование для других дат в формате 'ДД.ММ.ГГГГ'
                try:
                    data[key] = value.strftime("%d.%m.%Y")
                except ValueError:
                    logging.warning(f"Не удалось преобразовать значение {value} для ключа {key} в строку")
            elif key in DateTimeConverter.time_keys and isinstance(value, time):
                # Форматирование для времени в формате 'ЧЧ:ММ'
                try:
                    data[key] = value.strftime("%H:%M")
                except ValueError:
                    logging.warning(f"Не удалось преобразовать значение {value} для ключа {key} в строку")

        return data

    @staticmethod
    def convert_string_to_datetime(data: dict) -> dict:
        """
        Преобразует строки в объекты datetime и time для использования в приложении и при записи в БД.
        """
        for key, value in data.items():
            if key in DateTimeConverter.datetime_keys and isinstance(value, str):
                try:
                    data[key] = datetime.strptime(value, "%d.%m.%Y").date()
                except ValueError:
                    logging.warning(f"Не удалось преобразовать значение {value} для ключа {key} в datetime")

            elif key in DateTimeConverter.time_keys and isinstance(value, str):
                try:
                    data[key] = datetime.strptime(value, "%H:%M").time()
                except ValueError:
                    logging.warning(f"Не удалось преобразовать значение {value} для ключа {key} в time")

        return data

    @staticmethod
    def local_user_time(user_timezone, user_time_from_db):
        if 'UTC-' in user_timezone:
            hours_offset = int(user_timezone.split('UTC-')[1].split(':')[0])
            minutes_offset = int(user_timezone.split('UTC-')[1].split(':')[1])
            user_timezone = timezone(timedelta(hours=-hours_offset, minutes=-minutes_offset))
        elif 'UTC+' in user_timezone:
            hours_offset = int(user_timezone.split('UTC+')[1].split(':')[0])
            minutes_offset = int(user_timezone.split('UTC+')[1].split(':')[1])
            user_timezone = timezone(timedelta(hours=hours_offset, minutes=minutes_offset))

        local_user_time = user_time_from_db.astimezone(user_timezone)

        return local_user_time