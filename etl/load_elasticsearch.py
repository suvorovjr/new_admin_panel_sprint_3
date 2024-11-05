from typing import List

from backoff import expo, on_exception
from elasticsearch import Elasticsearch, exceptions, helpers
from schemas import FilmWork
from settings import app_logger

from etl import settings


@on_exception(
    expo,
    exceptions.ConnectionError,
    max_tries=10,
    max_time=100,
    logger=app_logger,
)
def get_elasticsearch_client() -> Elasticsearch:
    """Создает и возвращает экземпляр клиента Elasticsearch."""
    return Elasticsearch(
        [settings.ELASTICSEARCH_URL]
    )  # Используем URL из настроек


def create_bulk_action(film_work: FilmWork) -> dict:
    """Создает действие для bulk-загрузки в Elasticsearch."""
    return {
        '_index': settings.ELASTICSEARCH_INDEX_NAME,
        '_id': str(film_work.id),
        '_source': film_work.dict(),
    }


@on_exception(expo, exceptions.ConnectionError, max_tries=10, max_time=100, logger=app_logger)
def check_exists_index(es: Elasticsearch):
    """
    Проверяет существование индекса, если его нет, то попытается создать его
    :param es: экземпляр соединения с Elasticsearch
    Raises:
        exceptions.ConnectionError: Если возникла ошибка соединения при создании индекса.
        exceptions.BadRequestError: Если произошла ошибка с неправильным запросом при создании индекса.
    """
    index_name = settings.ELASTICSEARCH_INDEX_NAME

    if not es.indices.exists(index=index_name):
        app_logger.info(f'Индекса ElasticSearch с именем {index_name} не существует')
        try:
            es.indices.create(index=index_name, body=settings.ELASTICSEARCH_SCHEMA)
            app_logger.info()
        except exceptions.ConnectionError as e:
            app_logger.error(f'Ошибка соединения при создании индекса "{index_name}": {e}')
            raise
        except exceptions.BadRequestError as e:
            app_logger.error(f'Неправильный запрос при создании индекса "{index_name}": {e}')
            raise


def load_film_works_to_elasticsearch(film_works: List[FilmWork]) -> None:
    """Загружает список объектов FilmWork в Elasticsearch."""
    es = get_elasticsearch_client()
    bulk_film_works = [
        create_bulk_action(film_work) for film_work in film_works
    ]

    try:
        response = helpers.bulk(es, bulk_film_works)
        app_logger.info(f'Успешно проиндексировано {response[0]} документов.')
    except Exception as e:
        app_logger.error(f'Ошибка при индексации: {e}')
