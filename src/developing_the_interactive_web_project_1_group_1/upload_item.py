from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool
import os
import atexit


pool = None


def setup():
    global pool
    pool = ConnectionPool(
        os.environ["DATABASE_URL"], open=True, kwargs={"row_factory": dict_row}
    )
    atexit.register(pool.close)


def insert(img, emds):
    with pool.connection() as conn, conn.cursor() as curr:
        curr.execute(f"insert into test_image (image_data,embedding) values (%s, %s)", (img,emds))

def get_all():
    with pool.connection() as conn, conn.cursor() as curr:
        curr.execute(f"select id, image_data, embedding from test_image ")
        return curr.fetchall()
def get_one(id):
    with pool.connection() as conn, conn.cursor() as curr:
        curr.execute(f"select image_data from test_image where id=%s", (id,))
        row = curr.fetchone()
    return row

def make_test_table():
    with pool.connection() as conn, conn.cursor() as curr:
        curr.execute("create table test_image(id bigserial primary key, image_data bytea not null , embedding bytea not null)")
        # curr.execute("insert into test_table (name) values(%s)",("Boss",))
        # curr.execute("select name from test_table order by id desc")
        # return curr.fetchone()["name"]  

def erase_test_table(name):
     with pool.connection() as conn, conn.cursor() as curr:
        curr.execute(f"drop table {name}")
     
# def save_test_item(title,description,location, item_type, image_paths):
#     with pool.connection() as conn, conn.cursor() as curr:
#         curr.execute("create table if not exists test_items (id serial primary key, name text not null)")
#         curr.execute("insert into test_items (title,description,location,item_type) values(%s,%s,%s,%s) returning id",(title,description,location, item_type))
#         item_id = curr.fetchone()[0]
#         for path in image_paths
#         curr.execute("select name from test_table order by id desc")
#         return curr.fetchone()["name"] 


if __name__ == "__main__":
    import dotenv
    dotenv.load_dotenv()
    setup()
    print(make_test_table())
    # erase_test_table("test_image")