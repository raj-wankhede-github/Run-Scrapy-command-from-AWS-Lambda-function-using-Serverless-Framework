import os
from loguru import logger
import mysql.connector


# AWS Configurations
endpoint = os.getenv("ENDPOINT", "sql-new.cscogn5rp4fq.ap-south-1.rds.amazonaws.com")
username = os.getenv("USERNAME", "admin")
# username = "admin"
password = os.getenv("PASSWORD", "admin123")
database_name = os.getenv("DATABASE_NAME", "dbnews")
table_name = "news_data"


class DBOperations:
    def __init__(self, USERNAME=username, PASSWORD=password, HOST=endpoint, PORT=3306, DATABASE_NAME=database_name):
        self.USERNAME = USERNAME
        self.PASSWORD = PASSWORD
        self.HOST = HOST
        self.PASSWORD = PASSWORD
        self.DATABASE_NAME = DATABASE_NAME
        self.dbConn=None

    def connect(self):
        dbConn=None
        try:
            dbConn = mysql.connector.connect(
                user=username,
                password=password,
                host=endpoint,
                port=3306,
                database=database_name,
            )
            self.dbConn=dbConn
        except Exception as exc:
            logger.exception(f"Unable to connect:- {exc}")
        return dbConn

    def getDBVersion(self):
        try:
            cursor = self.dbConn.cursor()
            cursor.execute("SELECT VERSION()")
            print("DB Version: %s" % cursor.fetchone())
        except Exception as exc:
            print(f"DB Exception:- {exc}")
    
    def close(self):
        try:
            self.dbConn.close()
        except Exception as exc:
            logger.exception(f"Unable to close the connection:- {exc}")

    def commit(self):
        try:
            self.dbConn.commit()
        except Exception as exc:
            logger.exception(f"Unable to commit:- {exc}")

    def insert(self, new_json: dict):
        try:
            insert_query = f"""INSERT INTO {table_name} 
            (id, article_content, author, date, image_url, summary, title, domain_name) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"""

            data = (
                str(new_json['id']),
                str(new_json['article_content']),
                str(new_json['author']),
                str(new_json['date']),
                str(new_json['image_url']),
                str(new_json['summary']),
                str(new_json['title']),
                str(new_json['domain_name'])
            )

            cursor = self.dbConn.cursor()
            cursor.execute(insert_query, data)
            self.dbConn.commit()
        except Exception as exc:
            logger.exception(exc)

    def fetch_last_data(self, domain_name):
        try:
            fetch_query = (
                f"""SELECT date FROM {table_name} nd WHERE domain_name = '{domain_name}' ORDER BY date DESC LIMIT 1;"""
            )

            cursor = self.dbConn.cursor()
            cursor.execute(fetch_query)
            results = cursor.fetchall()

            if len(results) > 0:
                last_result_data = results[0]

                return last_result_data

        except Exception as exc:
            logger.exception(exc)
        return None
    
    def getMaxSeq(self):
        try:
            query = f"select max(id) from {table_name} nd;"
            cursor = self.dbConn.cursor()
            cursor.execute(query)
            result = cursor.fetchone()

            if result[0] is None:
                result = 0
            else:
                result = result[0]
        except Exception as e:
            logger.exception(f"Unable to fetch Maxid:- {e}")
        return result