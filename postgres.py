import psycopg2
from db.db import Connection


class PostgresConnection(Connection):
    def __init__(self, dbname, user, password, host, port):
        self.conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        self.cursor = self.conn.cursor()

    def insert_image_path(self, username, path):
        self.cursor.execute(
            "INSERT INTO uploaded_images (username, image_path) VALUES (%s, %s);",
            (username, path)
        )
        self.conn.commit()

    def close(self):
        self.cursor.close()
        self.conn.close()
