from elasticsearch import Elasticsearch, helpers
from typing import List
from etl import settings
from schemas import FilmWork
from settings import app_logger


def get_elasticsearch_client() -> Elasticsearch:
    """Создает и возвращает экземпляр клиента Elasticsearch."""
    return Elasticsearch([settings.ELASTICSEARCH_URL])  # Используем URL из настроек


def create_bulk_action(film_work: FilmWork) -> dict:
    """Создает действие для bulk-загрузки в Elasticsearch."""
    return {
        '_index': settings.ELASTICSEARCH_INDEX_NAME,
        '_id': str(film_work.id),
        '_source': film_work.dict()
    }


def load_film_works_to_elasticsearch(film_works: List[FilmWork]) -> None:
    """Загружает список объектов FilmWork в Elasticsearch."""
    es = get_elasticsearch_client()
    bulk_film_works = [create_bulk_action(film_work) for film_work in film_works]

    try:
        response = helpers.bulk(es, bulk_film_works)
        app_logger.info(f'Успешно проиндексировано {response[0]} документов.')
    except Exception as e:
        app_logger.error(f'Ошибка при индексации: {e}')
