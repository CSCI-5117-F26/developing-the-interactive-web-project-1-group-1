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

def get_user(user_id):
    pool.open()
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
            return cur.fetchone()

def get_image(photo_id):
    pool.open()
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM images WHERE photo_id = %s", (photo_id,))
            return cur.fetchone()

def get_posts(search=None, location_id=None, item_id=None, limit=20):
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

    pool.open()
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
    pool.open()
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM posts WHERE post_id = %s", (post_id,))
            return cur.fetchone()

def get_posts_for_user(user_id):
    pool.open()
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

def update_post(post_id, user_id, title, description, location_id, item_id, image_name=None, image_data=None):
    pool.open()
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """UPDATE posts SET title = %s, description = %s, tag_location = %s, tag_item = %s
                   WHERE post_id = %s AND user_id = %s
                   RETURNING photo_id""",
                (title, description, location_id, item_id, post_id, user_id),
            )
            row = cur.fetchone()
            if row is not None and image_data is not None:
                cur.execute(
                    "UPDATE images SET image_name = %s, image_data = %s WHERE photo_id = %s",
                    (image_name, image_data, row['photo_id']),
                )

def delete_post(post_id, user_id):
    pool.open()
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM posts WHERE post_id = %s AND user_id = %s RETURNING photo_id",
                        (post_id, user_id))
            row = cur.fetchone()
            if row is not None:
                cur.execute("DELETE FROM images WHERE photo_id = %s", (row['photo_id'],))
