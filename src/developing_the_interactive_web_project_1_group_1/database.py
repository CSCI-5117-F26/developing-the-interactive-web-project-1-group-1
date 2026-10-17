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
def insert_post(request):
    # need validation for all of this user input. Also we may want consistent
    # names in the html and db columns.
    image_data = request.files['photo'].read()
    filename = request.files['photo'].filename
    description = request.form.get('details')
    title = request.form.get('title')
    building = request.form.get('building')
    item_type = request.form.get('item_type')

    # hardcoding user id for techshare
    user_id = 6767
        
    global pool
    pool.open()
    with pool.connection() as conn:
        with conn.cursor() as cur:
            # first get the image into the db successfully 
            cur.execute("INSERT INTO images (image_name, image_data) VALUES (%s, %s) RETURNING photo_id", (filename, image_data))
            # the cursor will return a valid photo_id if successful 
            photo_id = cur.fetchone()['photo_id']

            # get the ids associated with the chosen location and item types
            # (we probably could make our design better to avoid these queries
            # below). Also, trailing comma required for single params!
            cur.execute("SELECT location_id FROM tag_building WHERE building_name = %s", (building,))
            tag_location = cur.fetchone()['location_id']
            cur.execute("SELECT item_id FROM tag_itemtype WHERE item_name = %s", (item_type,))
            tag_item = cur.fetchone()['item_id']

            # insert the post!
            # debug - print all values of the future posts table row 
            print(f'user_id: {user_id}, photo_id: {photo_id}, title: {title}, tag_location: {tag_location}, tag_item: {tag_item}, description: {description}')
            # here goes nothing...also, this long line below should be cleaned up to
            # be pythonic
            cur.execute("INSERT INTO posts (user_id, photo_id, title, tag_location, tag_item, description) VALUES (%s, %s, %s, %s, %s, %s)", (user_id, photo_id, title, tag_location, tag_item, description))

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
