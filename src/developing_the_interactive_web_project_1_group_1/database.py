from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool
import psycopg
import os
import atexit
import dotenv

pool = None
POST_EXPIRY = "1 month"

#copied exsample code from kluver
dotenv.load_dotenv()
pool = ConnectionPool(os.environ["DATABASE_URL"], open=False, min_size=1, max_size=3, kwargs={"row_factory": dict_row})
atexit.register(pool.close)

#worry about context managers later, when we actually need to work with data... but use %s
#well later is now, lucky me :)

def get_buildings():
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM tag_building ORDER BY building_name")
            return cur.fetchall()

def get_item_types():
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM tag_itemtype ORDER BY item_id")
            return cur.fetchall()

def create_post(user_id, title, description, location_id, item_id, image_name, image_data, image_embedding=None):
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
            post_id = cur.fetchone()['post_id']
            if image_embedding is not None and image_embedding.size>0:
                embedding_bytes = image_embedding.tobytes()
                cur.execute(f"insert into image_embeddings (photo_id,embedding) values (%s, %s)", (photo_id,embedding_bytes))
            return post_id

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

def get_all_users():
    pool.open()
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM users ORDER BY user_id")
            return cur.fetchall()

def display_name_taken(display_name):
    pool.open()
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT user_id FROM users WHERE display_name = %s", (display_name,))
            return cur.fetchone() is not None

def update_display_name(user_id, display_name):
    pool.open()
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE users SET display_name = %s WHERE user_id = %s",
                        (display_name, user_id))

def get_image(photo_id):
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM images WHERE photo_id = %s", (photo_id,))
            return cur.fetchone()

def get_all_image_embeddings():
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT photo_id, embedding FROM image_embeddings")
            return cur.fetchall()

def get_posts(search=None, location_id=None, item_id=None, limit=20 , ranked_photo_ids=None, image_search = False):
    with pool.connection() as conn:
        with conn.cursor() as cur:
            if image_search:
                conditions = []
                params = []
                if search and ranked_photo_ids is None:
                    conditions.append("(posts.title ILIKE %s OR posts.description ILIKE %s)")
                    params += [f"%{search}%", f"%{search}%"]
                if location_id:
                    conditions.append("posts.tag_location = %s")
                    params.append(location_id)
                if item_id:
                    conditions.append("posts.tag_item = %s")
                    params.append(item_id)
                if ranked_photo_ids is not None:
                    if not ranked_photo_ids:
                        return []
                    conditions.append("posts.photo_id = ANY(%s)")
                    params.append(ranked_photo_ids)
                where = "WHERE " + " AND ".join(conditions) if conditions else ""

                order_by = (
                    "array_position(%s::int[], posts.photo_id)"
                    if ranked_photo_ids is not None
                    else "posts.created_at DESC"
                )
                if ranked_photo_ids is not None:
                    params.append(ranked_photo_ids)

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
                                ORDER BY {order_by}
                                LIMIT %s""",
                            params + [limit],
                        )
                        return cur.fetchall()
            fuzzy_ids = []
            if search and search.strip():
                conditions=["(posts.title %% %s OR posts.description %% %s OR posts.description ILIKE %s OR posts.title ILIKE %s)"]
                params = [search,search,f"%{search}%", f"%{search}%"]
                if location_id:
                    conditions.append("posts.tag_location = %s")
                    params.append(location_id)
                if item_id:
                        conditions.append("posts.tag_item = %s")
                        params.append(item_id)
                where = (" AND ".join(conditions) if conditions else "")

                cur.execute(
                                f"""SELECT posts.photo_id
                                    FROM posts
                                    WHERE 
                                    {where}
                                    ORDER BY GREATEST(
                                        similarity(posts.title, %s),
                                        similarity(COALESCE(posts.description, ''), %s)
                                    ) DESC, posts.created_at DESC
                                    LIMIT %s""",
                                params + [search,search,100],
                            )
                fuzzy_ids = [row["photo_id"] for row in cur.fetchall()]
            if search:
                scores = {}
                for ranked_list in (fuzzy_ids, ranked_photo_ids or []):
                    for rank, photo_id in enumerate(ranked_list, start=1):
                        scores[photo_id] = (scores.get(photo_id,0)+1/(60+rank))
                ranked_ids = sorted(scores, key=scores.get, reverse=True)
                if not ranked_ids: 
                    return []
                conditions = ["posts.photo_id = ANY(%s)"]
                params = [ranked_ids]
                    
                if location_id:
                    conditions.append("posts.tag_location = %s")
                    params.append(location_id)
                if item_id:
                    conditions.append("posts.tag_item = %s")
                    params.append(item_id)
                where = ("WHERE " + " AND ".join(conditions) if conditions else "")
                cur.execute(
                            f"""SELECT posts.post_id, posts.photo_id, posts.title, posts.created_at,
                                        tag_building.building_name, tag_itemtype.item_name, users.display_name
                                FROM posts
                                JOIN tag_building ON posts.tag_location = tag_building.location_id
                                JOIN tag_itemtype ON posts.tag_item = tag_itemtype.item_id
                                JOIN users ON posts.user_id = users.user_id
                                {where}
                                ORDER BY array_position(%s::int[], posts.photo_id)
                                LIMIT %s""",
                            params + [ranked_ids,limit],
                            )
                return cur.fetchall()
                
            else:    
                conditions = []
                params = []
                if location_id:
                    conditions.append("posts.tag_location = %s")
                    params.append(location_id)
                if item_id:
                    conditions.append("posts.tag_item = %s")
                    params.append(item_id)
                where = ("WHERE " + " AND ".join(conditions) if conditions else "")
        
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

def get_posts_for_user(user_id):
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT posts.post_id, posts.photo_id, posts.title, posts.description, posts.created_at,
                          tag_building.building_name, tag_itemtype.item_name,
                          COUNT(comments.comment_id) AS comment_count
                   FROM posts
                   JOIN tag_building ON posts.tag_location = tag_building.location_id
                   JOIN tag_itemtype ON posts.tag_item = tag_itemtype.item_id
                   LEFT JOIN comments ON comments.post_id = posts.post_id
                   WHERE posts.user_id = %s
                   GROUP BY posts.post_id, tag_building.building_name, tag_itemtype.item_name
                   ORDER BY posts.created_at DESC""",
                (user_id,),
            )
            return cur.fetchall()

def update_post(post_id, user_id, title, description, location_id, item_id, image_name=None, image_data=None):
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
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM posts WHERE post_id = %s AND user_id = %s RETURNING photo_id",
                        (post_id, user_id))
            row = cur.fetchone()
            if row is not None:
                cur.execute("DELETE FROM images WHERE photo_id = %s", (row['photo_id'],))

def delete_expired_posts():
    pool.open()
    with pool.connection() as conn:
        with conn.cursor() as cur:
            # TODO: delete associated comments

            # delete posts and return a list of orphaned photos
            cur.execute(
                """DELETE FROM posts
                   WHERE created_at < now() - %s::interval
                   RETURNING photo_id""",
                [POST_EXPIRY],
            )

            # delete orphaned photos 
            photo_ids = [row['photo_id'] for row in cur.fetchall()]
            cur.execute("DELETE FROM images WHERE photo_id = ANY(%s)", [photo_ids])
 
