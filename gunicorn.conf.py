from developing_the_interactive_web_project_1_group_1.database import pool


def post_fork(server, worker):
    print("FORKED!")
    pool.open()
    print("FORKED OPEN")
