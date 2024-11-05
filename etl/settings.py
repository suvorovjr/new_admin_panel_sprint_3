import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger

BASE_DIR = Path(__file__).resolve().parent
ENV_FILE_PATH = BASE_DIR / '.env'
LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

load_dotenv(ENV_FILE_PATH)


def get_env_variable(var_name, default=None, required=True):
    value = os.getenv(var_name, default)
    if required and value is None:
        raise EnvironmentError(f"The environment variable '{var_name}' is missing.")
    return value


def configure_logger():
    FORMATTER = '{time:YYYY-MM-DD HH:mm:ss} | {level} | {file}:{function}:{line} | {message}'
    logger.remove()  # Clear any existing loggers
    logger.add(sys.stdout, level='DEBUG', format=FORMATTER)
    logger.add(
        LOGS_DIR / 'etl_logger.log',
        level='INFO',
        format=FORMATTER,
        rotation='50 MB',
        compression='zip'
    )
    return logger


app_logger = configure_logger()

DSL = {
    'dbname': get_env_variable('POSTGRES_NAME'),
    'user': get_env_variable('POSTGRES_USER'),
    'password': get_env_variable('POSTGRES_PASSWORD'),
    'host': get_env_variable('POSTGRES_HOST'),
    'port': get_env_variable('POSTGRES_PORT'),
    'options': '-c search_path=content',
}

ELASTICSEARCH_URL = get_env_variable('ELASTICSEARCH_URL', required=False)
ELASTICSEARCH_INDEX_NAME = get_env_variable('ELASTICSEARCH_INDEX_NAME', required=False)

REDIS_HOST = get_env_variable('REDIS_HOST', default='localhost', required=False)
REDIS_PASSWORD = get_env_variable('REDIS_PASSWORD', required=False)
REDIS_PORT = int(get_env_variable('REDIS_PORT', default=6379, required=False))
REDIS_DB = int(get_env_variable('REDIS_DB', default=0, required=False))
