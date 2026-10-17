from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool
import os
import atexit

pool = None
#copied exsample code from kluver
def setup():
    global pool
    # open=false is the fix Kluver recommended for the DB issue
    pool = ConnectionPool(os.environ["DATABASE_URL"], open=False, kwargs={"row_factory": dict_row})
    atexit.register(pool.close)

#worry about context managers later, when we actually need to work with data... but use %s
#well later is now, lucky me :)
def get_buildings():
    pool.open()
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM tag_building ORDER BY building_name")
            return cur.fetchall()

def get_item_types():
    pool.open()
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM tag_itemtype ORDER BY item_name")
            return cur.fetchall()

def create_post(user_id, title, description, location_id, item_id, image_name, image_data):
    # validation happens in app.py before this is called. The form sends the
    # building and item type ids, so no lookups by name are needed here.
    pool.open()
    with pool.connection() as conn:
        with conn.cursor() as cur:
            # first get the image into the db successfully
            cur.execute(
                "INSERT INTO images (image_name, image_data) VALUES (%s, %s) RETURNING photo_id",
                (image_name, image_data),
            )
            # the cursor will return a valid photo_id if successful
            photo_id = cur.fetchone()['photo_id']

            # insert the post!
            cur.execute(
                """INSERT INTO posts (user_id, photo_id, title, tag_location, tag_item, description)
                   VALUES (%s, %s, %s, %s, %s, %s) RETURNING post_id""",
                (user_id, photo_id, title, location_id, item_id, description),
            )
            return cur.fetchone()['post_id']

def get_or_create_user(auth_id, display_name):
    pool.open()
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

def get_image(photo_id):
    pool.open()
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM images WHERE photo_id = %s", (photo_id,))
            return cur.fetchone()
