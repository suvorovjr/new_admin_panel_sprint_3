from datetime import datetime
from typing import List, Set
from uuid import UUID
import redis

import settings


class RedisStorage:
    DEFAULT_DATE = datetime(year=2024, month=1, day=1, hour=0, minute=0, second=0)

    def __init__(self):
        try:
            self.redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                password=settings.REDIS_PASSWORD,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB
            )
            self.last_check_date_key = 'last_check_date'
            self.check_status_key = 'check_status'
            self.ids_set_key = 'pending_ids'
        except redis.exceptions.RedisError as e:
            raise ConnectionError(f'Не удалось подключиться к Redis: {e}')

    def get_last_check_date(self) -> datetime:
        """
        Метод для получения даты последней проверки.
        :return: Дата последней проверки -> datetime
        """
        date_str = self.redis_client.get(self.last_check_date_key)
        if date_str is not None:
            return datetime.fromisoformat(date_str.decode())
        else:
            self.set_last_check_date(self.DEFAULT_DATE)
            return self.DEFAULT_DATE

    def set_last_check_date(self, date: datetime) -> None:
        """
        Устанавливает дату последней проверки.
        :param date: Дата последней проверки.
        """
        self.redis_client.set(self.last_check_date_key, date.isoformat())

    def get_check_status(self) -> str:
        """
        Получает статус проверки.
        :return: Статус проверки (по умолчанию "not_completed").
        """
        status = self.redis_client.get(self.check_status_key)
        return status.decode() if status else 'not_completed'

    def set_check_status(self, status: str) -> None:
        """
        Устанавливает статус проверки.
        :param status: Новый статус проверки.
        """
        self.redis_client.set(self.check_status_key, status)

    def add_ids(self, ids: List[UUID]) -> None:
        """
        Добавляет список уникальных ID в Redis.
        :param ids: Список уникальных ID.
        """
        if ids:
            self.redis_client.sadd(self.ids_set_key, *[str(id_) for id_ in ids])

    def get_all_ids(self) -> Set[UUID]:
        """
        Получает все ID из Redis.
        :return: Множество уникальных ID.
        """
        return {UUID(id_str.decode()) for id_str in self.redis_client.smembers(self.ids_set_key)}

    def remove_ids_batch(self, ids: List[UUID]) -> None:
        """
        Удаляет список ID из Redis.
        :param ids: Список ID для удаления.
        """
        if ids:
            self.redis_client.srem(self.ids_set_key, *[str(id_) for id_ in ids])

    def set_completed_status(self) -> None:
        """
        Завершает проверку, устанавливая статус на "completed"
        """
        self.set_check_status('completed')

    def set_check_data(self) -> None:
        """
        Обновляет дату проверки
        """
        self.set_last_check_date(datetime.now())
