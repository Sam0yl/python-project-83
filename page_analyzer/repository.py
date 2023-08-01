import os
import datetime
import psycopg2
from page_analyzer.url import Url
from page_analyzer.check import CheckData
from dotenv import load_dotenv


load_dotenv()  # take environment variables from .env
DATABASE_URL = os.getenv('DATABASE_URL')


class UrlRepository():

    def connect(self):
        conn = psycopg2.connect(DATABASE_URL)
        return conn

    def is_url_in_repository(self, url):
        conn = self.connect()
        with conn.cursor() as curs:
            curs.execute(
                'SELECT name FROM urls WHERE name=%s',
                (url.name,))
            result = curs.fetchall()
        conn.close()
        if not result:
            return False
        return True

    def add_url(self, url):
        if not self.is_url_in_repository(url):
            conn = self.connect()
            with conn.cursor() as curs:
                created_at = str(datetime.date.today())
                curs.execute(
                    'INSERT INTO urls (name, created_at) VALUES (%s, %s)',
                    (url.name, created_at))
            conn.commit()
            conn.close()

    def assign_url_id(self, url):
        if self.is_url_in_repository(url):
            conn = self.connect()
            with conn.cursor() as curs:
                curs.execute(
                    'SELECT id, created_at FROM urls WHERE name=%s',
                    (url.name,))
                url_data = curs.fetchall()
            conn.close()
        id, created_at = url_data[0]
        url.set_id(id)
        url.set_created_at(created_at)

    def get_url_by_id(self, url_id):
        conn = self.connect()
        with conn.cursor() as curs:
            curs.execute(
                'SELECT name, created_at FROM urls WHERE id=%s',
                (url_id,))
            url_data = curs.fetchall()
        conn.close()
        name, created_at = url_data[0]
        return Url(name, url_id, str(created_at))

    def get_urls(self):
        conn = self.connect()
        with conn.cursor() as curs:
            curs.execute('SELECT * FROM urls')
            db_url_data = curs.fetchall()
        conn.close()
        db_url_data.reverse()
        urls = [Url(name, id, created_at)
                for id, name, created_at in db_url_data]
        for url in urls:
            url.set_last_check(self.get_last_url_check(url.id))
        return urls

    def add_url_check(self, check):
        conn = self.connect()
        with conn.cursor() as curs:
            curs.execute(
                """INSERT INTO url_checks (url_id, created_at, status_code,
                title, h1, description) VALUES (%s, %s, %s, %s, %s, %s)""",
                (check.url_id, check.created_at, check.code, check.title,
                 check.h1, check.description))
        conn.commit()
        conn.close()

    def get_url_checks(self, url_id):
        conn = self.connect()
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
        conn = self.connect()
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
