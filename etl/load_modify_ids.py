from datetime import datetime
from typing import List
from uuid import UUID

import psycopg
from pg_queries import get_all_modify_ids_query
from settings import app_logger


def get_all_modify_film_works(
    pg_cursor: psycopg.Cursor, last_update: datetime
) -> List[UUID]:
    """
    Извлекает все ID фильмов, которые были изменены после заданной даты.

    Args:
        pg_cursor (psycopg.Cursor): Курсор для выполнения запросов к базе данных.
        last_update (datetime): Дата последней загрузки данных.
        Все фильмы, поля которых были изменены после этой даты, будут извлечены.

    Returns:
        List[UUID]: Список UUID фильмов, которые были изменены.
    """
    try:
        pg_cursor.execute(
            get_all_modify_ids_query, (last_update, last_update, last_update)
        )
        modified_film_work_ids = [row['id'] for row in pg_cursor.fetchall()]
        app_logger.info(
            f'Извлечено {len(modified_film_work_ids)} измененных фильмов после {last_update.isoformat()}'
        )
        return modified_film_work_ids
    except psycopg.Error as e:
        app_logger.error(f'Ошибка при извлечении измененных фильмов: {e}')
        return []
