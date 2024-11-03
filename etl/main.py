from contextlib import closing
import psycopg
import settings
from psycopg.rows import dict_row
from redis_storage import RedisStorage
from exstract_postgres import transform_data


def main():
    storage = RedisStorage()
    last_status = storage.get_check_status()
    if last_status:
    with closing(psycopg.connect(**settings.DSL)) as pg_conn:
        with closing(pg_conn.cursor(row_factory=dict_row)) as pg_cur:
            film_work_ids = get_modify_film_works(pg_cur)
            for row in transform_data(pg_cursor=pg_cur, film_work_ids=film_work_ids, batch_size=100):
                load_es(row)


