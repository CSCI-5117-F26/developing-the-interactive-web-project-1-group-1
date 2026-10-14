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

def get_or_create_user(auth_id, display_name):
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM users WHERE auth_id = %s", (auth_id,))
            user = cur.fetchone()
            if user is None:
                cur.execute(
                    "INSERT INTO users (auth_id, display_name) VALUES (%s, %s) RETURNING *",
                    (auth_id, display_name),
                )
                user = cur.fetchone()
            return user