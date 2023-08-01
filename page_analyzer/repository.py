import os
import datetime
import psycopg2
from page_analyzer.url import Url
from page_analyzer.check import CheckData
from dotenv import load_dotenv


load_dotenv()  # take environment variables from .env
DATABASE_URL = os.getenv('DATABASE_URL')


def connect_db():
    connect = psycopg2.connect(DATABASE_URL)
    return connect


def execute_sql_query(connect, query, params=None):
    with connect.cursor() as curs:
        curs.execute(query, params)
        try:
            result = curs.fetchall()
            return result
        except Exception:
            return


class UrlRepository():

    def is_url_in_repository(self, url):
        conn = connect_db()
        result = execute_sql_query(
            conn,
            'SELECT name FROM urls WHERE name=%s',
            (url.name,))
        conn.close()
        if not result:
            return False
        return True

    def add_url(self, url):
        if not self.is_url_in_repository(url):
            conn = connect_db()
            created_at = str(datetime.date.today())
            execute_sql_query(
                conn,
                'INSERT INTO urls (name, created_at) VALUES (%s, %s)',
                (url.name, created_at))
            conn.commit()
            conn.close()

    def assign_url_id(self, url):
        if self.is_url_in_repository(url):
            conn = connect_db()
            url_data = execute_sql_query(
                conn,
                'SELECT id, created_at FROM urls WHERE name=%s',
                (url.name,))
            conn.close()
        id, created_at = url_data[0]
        url.id = id
        url.created_at = created_at

    def get_url_by_id(self, url_id):
        conn = connect_db()
        url_data = execute_sql_query(
            conn,
            'SELECT name, created_at FROM urls WHERE id=%s',
            (url_id,))
        conn.close()
        name, created_at = url_data[0]
        return Url(name, url_id, str(created_at))

    def get_urls(self):
        conn = connect_db()
        urls_data = execute_sql_query(
            conn,
            'SELECT * FROM urls')
        conn.close()
        urls_data.reverse()
        urls = [Url(name, id, created_at)
                for id, name, created_at in urls_data]
        for url in urls:
            url.set_last_check(self.get_last_url_check(url.id))
        return urls

    def add_url_check(self, check):
        conn = connect_db()
        execute_sql_query(
            conn,
            """INSERT INTO url_checks (url_id, created_at, status_code,
            title, h1, description) VALUES (%s, %s, %s, %s, %s, %s)""",
            (check.url_id, check.created_at, check.code,
             check.title, check.h1, check.description))
        conn.commit()
        conn.close()

    def get_url_checks(self, url_id):
        conn = connect_db()
        with conn.cursor() as curs:
            curs.execute('SELECT * FROM url_checks WHERE url_id=%s', (url_id,))
            db_data = curs.fetchall()
            db_columns = [desc[0] for desc in curs.description]
        conn.close()
        db_data.reverse()
        checks_values = [dict(zip(db_columns, values)) for values in db_data]
        checks = [CheckData(data=values) for values in checks_values]
        return checks

    def get_last_url_check(self, url_id):
        conn = connect_db()
        with conn.cursor() as curs:
            curs.execute(
                'SELECT * FROM url_checks WHERE url_id=%s \
                ORDER BY id DESC LIMIT 1',
                (url_id,))
            db_data = curs.fetchone()
            db_columns = [desc[0] for desc in curs.description]
        conn.close()
        if not db_data:
            return CheckData()
        check_values = dict(zip(db_columns, db_data))
        return CheckData(data=check_values)
