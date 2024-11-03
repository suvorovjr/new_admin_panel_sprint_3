import os
from pathlib import Path

import redis
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
ENV_FILE_PATH = BASE_DIR / '.env'

load_dotenv(ENV_FILE_PATH)

DSL = {
    'dbname': os.environ.get('POSTGRES_NAME'),
    'user': os.environ.get('POSTGRES_USER'),
    'password': os.environ.get('POSTGRES_PASSWORD'),
    'host': os.environ.get('POSTGRES_HOST'),
    'port': os.environ.get('POSTGRES_PORT'),
    'options': '-c search_path=content',
}

ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL')

REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD')
REDIS_PORT = os.environ.get('REDIS_PORT', 6379)
REDIS_DB = os.environ.get('REDIS_DB', 0)


def get_redis_connection() -> redis.Redis:
    """
    Функция для создания и получения соединения с Redis
    """
    try:
        redis_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            password=REDIS_PASSWORD
        )
        if redis_client.ping():
            print('Все ок заглушка')
            return redis_client
    except ConnectionError as e:
        raise Exception("Не удалось подключиться к Redis: " + str(e))
