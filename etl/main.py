from contextlib import closing
import psycopg
import settings
from psycopg.rows import dict_row
from load_elasticsearch import load_film_works_to_elasticsearch
from etl.load_modify_ids import get_all_modify_film_works
from redis_storage import RedisStorage
from exstract_postgres import transform_data
from settings import app_logger

# Статусы проверки
STATUS_NOT_STARTED = 'NOT_STARTED'
STATUS_IN_PROGRESS = 'IN_PROGRESS'
STATUS_COMPLETED = 'COMPLETED'


def process_in_progress(pg_cur, storage):
    """Обрабатывает фильмы в состоянии 'IN_PROGRESS'."""
    modify_film_work_ids = storage.get_all_ids()
    for row in transform_data(pg_cursor=pg_cur, film_work_ids=modify_film_work_ids, batch_size=100):
        load_film_works_to_elasticsearch(film_works=row)
        remove_redis_ids = [field.id for field in row]
        storage.remove_ids_batch(ids=remove_redis_ids)
    storage.set_check_status(STATUS_COMPLETED)


def main():
    storage = RedisStorage()

    with closing(psycopg.connect(**settings.DSL)) as pg_conn:
        with closing(pg_conn.cursor(row_factory=dict_row)) as pg_cur:
            last_status = storage.get_check_status()

            try:
                if last_status == STATUS_NOT_STARTED:
                    last_check_date = storage.get_last_check_date()
                    modify_film_work_ids = get_all_modify_film_works(pg_cursor=pg_cur, last_update=last_check_date)
                    storage.add_ids(modify_film_work_ids)
                    storage.set_check_data()
                    storage.set_check_status(STATUS_IN_PROGRESS)

                last_status = storage.get_check_status()
                if last_status == STATUS_IN_PROGRESS:
                    process_in_progress(pg_cur, storage)

                last_status = storage.get_check_status()
                if last_status == STATUS_COMPLETED:
                    storage.set_check_status(STATUS_NOT_STARTED)

            except Exception as e:
                app_logger.error(f'Ошибка в процессе ETL: {e}')


if __name__ == '__main__':
    main()
