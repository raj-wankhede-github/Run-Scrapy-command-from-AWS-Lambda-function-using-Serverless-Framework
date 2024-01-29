import os
from loguru import logger
import mysql.connector


# AWS Configurations
endpoint = os.getenv("ENDPOINT", "sql-new.cscogn5rp4fq.ap-south-1.rds.amazonaws.com")
username = os.getenv("USERNAME", "admin")
password = os.getenv("PASSWORD", "admin123")
database_name = os.getenv("DATABASE_NAME", "news_data")


class DBOperations:
    def __init__(self) -> None:
        self.connection = self.get_db_connection()
        self.cursor = self.get_cursor()

    def get_db_connection(self):
        try:
            self.connection = mysql.connector.connect(
                user=username,
                password=password,
                host=endpoint,
                port=3306,
                database=database_name,
            )

            return self.connection
        except Exception as exc:
            logger.exception(f"Unable to connect:- {exc}")
        return None

    def get_cursor(self):
        self.cursor = self.connection.cursor()
        return self.cursor

    def commit(self):
        self.connection.commit()

    def db_insert(self, new_json: dict):
        try:
            insert_query = f"""INSERT INTO {database_name} (article_content, author, date, image_url, summary, title)
            VALUES
            ({new_json['article_content']}, 
            {new_json['author']}, 
            {new_json['date']}, 
            {new_json['image_url']}, 
            {new_json['summary']}, 
            {new_json['title']});
            """

            self.cursor.execute(insert_query)
            self.commit()
        except Exception as exc:
            logger.exception(exc)

    def fetch_last_data(self):
        try:
            fetch_query = (
                f"""SELECT date FROM {database_name} ORDER BY id DESC LIMIT 1;"""
            )

            self.cursor.execute(fetch_query)
            results = self.cursor.fetchall()

            if len(results) > 0:
                last_result_data = results[0]

                return last_result_data

        except Exception as exc:
            logger.exception(exc)
        return None
