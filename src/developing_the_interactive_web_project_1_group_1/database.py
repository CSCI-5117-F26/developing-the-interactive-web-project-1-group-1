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

def get_user(user_id):
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
            return cur.fetchone()

def get_buildings():
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM tag_building ORDER BY building_name")
            return cur.fetchall()

def get_item_types():
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM tag_itemtype ORDER BY item_name")
            return cur.fetchall()

def create_post(user_id, title, description, location_id, item_id, image_name, image_data):
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO images (image_name, image_data) VALUES (%s, %s) RETURNING photo_id",
                (image_name, image_data),
            )
            photo_id = cur.fetchone()['photo_id']
            cur.execute(
                """INSERT INTO posts (user_id, photo_id, title, tag_location, tag_item, description)
                   VALUES (%s, %s, %s, %s, %s, %s) RETURNING post_id""",
                (user_id, photo_id, title, location_id, item_id, description),
            )
            return cur.fetchone()['post_id']

def get_posts_for_user(user_id):
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT posts.post_id, posts.photo_id, posts.title, tag_building.building_name,
                          COUNT(comments.comment_id) AS comment_count
                   FROM posts
                   JOIN tag_building ON posts.tag_location = tag_building.location_id
                   LEFT JOIN comments ON comments.post_id = posts.post_id
                   WHERE posts.user_id = %s
                   GROUP BY posts.post_id, tag_building.building_name
                   ORDER BY posts.created_at DESC""",
                (user_id,),
            )
            return cur.fetchall()

def get_posts(search=None, location_id=None, item_id=None, limit=20):
    # build the WHERE part from whichever filters were given
    conditions = []
    params = []
    if search:
        conditions.append("(posts.title ILIKE %s OR posts.description ILIKE %s)")
        params += [f"%{search}%", f"%{search}%"]
    if location_id:
        conditions.append("posts.tag_location = %s")
        params.append(location_id)
    if item_id:
        conditions.append("posts.tag_item = %s")
        params.append(item_id)
    where = "WHERE " + " AND ".join(conditions) if conditions else ""

    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""SELECT posts.post_id, posts.photo_id, posts.title, posts.created_at,
                           tag_building.building_name, tag_itemtype.item_name, users.display_name
                    FROM posts
                    JOIN tag_building ON posts.tag_location = tag_building.location_id
                    JOIN tag_itemtype ON posts.tag_item = tag_itemtype.item_id
                    JOIN users ON posts.user_id = users.user_id
                    {where}
                    ORDER BY posts.created_at DESC
                    LIMIT %s""",
                params + [limit],
            )
            return cur.fetchall()

def get_post(post_id):
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM posts WHERE post_id = %s", (post_id,))
            return cur.fetchone()

def delete_post(post_id):

    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM posts WHERE post_id = %s RETURNING photo_id", (post_id,))
            photo_id = cur.fetchone()['photo_id']
            cur.execute("DELETE FROM images WHERE photo_id = %s", (photo_id,))

def get_image(photo_id):
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM images WHERE photo_id = %s", (photo_id,))
            return cur.fetchone()