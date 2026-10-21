from lec3.database import pool


def post_fork(server, worker):
    pool.open()
