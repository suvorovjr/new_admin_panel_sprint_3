from uuid import UUID
from pg_queries import get_all_modify_ids_query
from typing import List
from datetime import datetime
import psycopg


def get_all_modify_film_works(pg_cursor: psycopg.Cursor, data: datetime) -> List[UUID]:
    """
    Извлекает все id фильмов, которые были изменены после заданной даты.
    Args:
        pg_cursor (psycopg.Cursor): Курсор для выполнения запросов к базе данных.
        data (datetime): Дата последней загрузку данных. Все фильмы, поля которых были изменены после этой даты, будут извлечены.
    Returns:
        List[UUID]: Список UUID фильмов, которые были изменены.
    """

    pg_cursor.execute(get_all_modify_ids_query, (data, data, data))
    modified_film_work_ids = [row['id'] for row in pg_cursor.fetchall()]
    return modified_film_work_ids
