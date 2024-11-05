import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from loguru import logger

BASE_DIR = Path(__file__).resolve().parent
ENV_FILE_PATH = BASE_DIR.parent / '.env'
LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

load_dotenv(ENV_FILE_PATH)


def get_env_variable(var_name, default=None, required=True):
    value = os.getenv(var_name, default)
    if required and value is None:
        raise EnvironmentError(
            f'Отсутствует переменная окружения "{var_name}".'
        )
    return value


def configure_logger():
    formatter = '{time:YYYY-MM-DD HH:mm:ss} | {level} | {file}:{function}:{line} | {message}'
    logger.remove()
    logger.add(sys.stdout, level='DEBUG', format=formatter)
    logger.add(
        LOGS_DIR / 'etl_logger.log',
        level='INFO',
        format=formatter,
        rotation='50 MB',
        compression='zip',
    )
    return logger


app_logger = configure_logger()

DSL = {
    'dbname': get_env_variable('POSTGRES_DB'),
    'user': get_env_variable('POSTGRES_USER'),
    'password': get_env_variable('POSTGRES_PASSWORD'),
    'host': get_env_variable('SQL_HOST'),
    'port': get_env_variable('SQL_PORT'),
    'options': '-c search_path=content',
}

REDIS_HOST = get_env_variable(
    'REDIS_HOST', default='localhost', required=False
)
REDIS_PASSWORD = get_env_variable('REDIS_PASSWORD', required=False)
REDIS_PORT = int(get_env_variable('REDIS_PORT', default=6379, required=False))
REDIS_DB = int(get_env_variable('REDIS_DB', default=0, required=False))

ELASTICSEARCH_URL = get_env_variable('ELASTICSEARCH_URL', required=False)
ELASTICSEARCH_INDEX_NAME = get_env_variable(
    'ELASTICSEARCH_INDEX_NAME', required=False
)
ELASTICSEARCH_SCHEMA = {
    'settings': {
        'refresh_interval': '1s',
        'analysis': {
            'filter': {
                'english_stop': {'type': 'stop', 'stopwords': '_english_'},
                'english_stemmer': {'type': 'stemmer', 'language': 'english'},
                'english_possessive_stemmer': {
                    'type': 'stemmer',
                    'language': 'possessive_english',
                },
                'russian_stop': {'type': 'stop', 'stopwords': '_russian_'},
                'russian_stemmer': {'type': 'stemmer', 'language': 'russian'},
            },
            'analyzer': {
                'ru_en': {
                    'tokenizer': 'standard',
                    'filter': [
                        'lowercase',
                        'english_stop',
                        'english_stemmer',
                        'english_possessive_stemmer',
                        'russian_stop',
                        'russian_stemmer',
                    ],
                }
            },
        },
    },
    'mappings': {
        'dynamic': 'strict',
        'properties': {
            'id': {'type': 'keyword'},
            'imdb_rating': {'type': 'float'},
            'genres': {'type': 'keyword'},
            'title': {
                'type': 'text',
                'analyzer': 'ru_en',
                'fields': {'raw': {'type': 'keyword'}},
            },
            'description': {'type': 'text', 'analyzer': 'ru_en'},
            'directors_names': {'type': 'text', 'analyzer': 'ru_en'},
            'actors_names': {'type': 'text', 'analyzer': 'ru_en'},
            'writers_names': {'type': 'text', 'analyzer': 'ru_en'},
            'directors': {
                'type': 'nested',
                'dynamic': 'strict',
                'properties': {
                    'id': {'type': 'keyword'},
                    'name': {'type': 'text', 'analyzer': 'ru_en'},
                },
            },
            'actors': {
                'type': 'nested',
                'dynamic': 'strict',
                'properties': {
                    'id': {'type': 'keyword'},
                    'name': {'type': 'text', 'analyzer': 'ru_en'},
                },
            },
            'writers': {
                'type': 'nested',
                'dynamic': 'strict',
                'properties': {
                    'id': {'type': 'keyword'},
                    'name': {'type': 'text', 'analyzer': 'ru_en'},
                },
            },
        },
    },
}
