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


def execute_sql_query(connect, query, params=None, columns=False):
    with connect.cursor() as curs:
        curs.execute(query, params)
        try:
            values = curs.fetchall()
            if columns:
                columns = [desc[0] for desc in curs.description]
                result = [dict(zip(columns, value)) for value in values]
                return result
            return values
        except Exception:
            return


class UrlRepository():

    def url_in_repository(self, url):
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
        if not self.url_in_repository(url):
            conn = connect_db()
            created_at = str(datetime.date.today())
            execute_sql_query(
                conn,
                'INSERT INTO urls (name, created_at) VALUES (%s, %s)',
                (url.name, created_at))
            conn.commit()
            conn.close()

    def assign_url_id(self, url):
        if self.url_in_repository(url):
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
        url_checks_data = execute_sql_query(
            conn,
            'SELECT * FROM url_checks WHERE url_id=%s',
            (url_id,),
            columns=True)
        conn.close()
        url_checks_data.reverse()
        return [CheckData(data=values) for values in url_checks_data]

    def get_last_url_check(self, url_id):
        conn = connect_db()
        last_check_data = execute_sql_query(
            conn,
            """SELECT * FROM url_checks WHERE url_id=%s
             ORDER BY id DESC LIMIT 1""",
            (url_id,),
            columns=True)
        conn.close()
        if not last_check_data:
            return CheckData()
        return CheckData(data=last_check_data[0])
