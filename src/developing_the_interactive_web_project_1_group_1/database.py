from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool
import os
import atexit

pool = None
#copied exsample code from kluver
def setup():
    global pool
    pool = ConnectionPool(os.environ["DATABASE_URL"], open=True, kwargs={"row_factory": dict_row})
    atexit.register(pool.close)

#worry about context managers later, when we actually need to work with data... but use %s
#well later is now, lucky me :)
def insert_image(filename, image_data):
    global pool
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO images (image_name, image_data) VALUES (%s, %s)", (filename, image_data))
