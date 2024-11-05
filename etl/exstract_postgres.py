from typing import Any, Generator, List
from uuid import UUID

import backoff
import psycopg
from pg_queries import get_film_works_query
from psycopg import OperationalError
from schemas import FilmWork


@backoff.on_exception(
    backoff.expo, psycopg.OperationalError, max_tries=5, jitter=None
)
def extract_data(
    pg_cursor: psycopg.Cursor, film_work_ids: List[UUID], batch_size: int = 100
) -> Generator[List[dict[str, Any]], None, None]:
    """
    Извлекает данные о фильмах из базы данных PostgreSQL с использованием курсора.

    Args:
        pg_cursor (psycopg.Cursor): Курсор для выполнения запросов к базе данных.
        film_work_ids (List[UUID]): Список идентификаторов фильмов для извлечения.
        batch_size (int): Размер пакета для выборки данных (по умолчанию 100).

    Yields:
        Generator[List[dict[str, Any]], None, None]: Генератор, выдающий пакеты данных.
    """
    query = get_film_works_query
    try:
        pg_cursor.execute(query, (film_work_ids,))
    except psycopg.OperationalError as e:
        raise OperationalError('Сбой операции с базой данных') from e

    while result := pg_cursor.fetchmany(batch_size):
        yield result


def transform_data(
    pg_cursor: psycopg.Cursor, film_work_ids: List[UUID], batch_size: int = 100
) -> Generator[list[FilmWork], None, None]:
    """
    Преобразует извлеченные данные в модели Pydantic.

    Args:
        pg_cursor (psycopg.Cursor): Курсор для выполнения запросов к базе данных.
        film_work_ids (List[UUID]): Список идентификаторов фильмов для извлечения.
        batch_size (int): Размер пакета для выборки данных (по умолчанию 100).

    Yields:
        Generator[List[FilmWork], None, None]: Генератор, выдающий модели FilmWork.
    """
    for batch in extract_data(
        pg_cursor=pg_cursor, film_work_ids=film_work_ids, batch_size=batch_size
    ):
        yield [FilmWork(**row) for row in batch]
