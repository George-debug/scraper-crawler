import psycopg2

with open("DATABASE_INFO.txt", "r") as f:
    host, user, password = f.read().splitlines()


CONN = psycopg2.connect(
    database="cool_data",
    user=user,
    password=password,
    host=host,
    port="5432"
)

CURSOR = CONN.cursor()
