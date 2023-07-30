import os
import datetime
import psycopg2
#  from dotenv import load_dotenv


#  load_dotenv()  # take environment variables from .env
DATABASE_URL = os.getenv('DATABASE_URL')


class Url():
    def __init__(self, name, id='', created_at=''):
        self.name = name
        self.id = id
        self.created_at = created_at

    def __str__(self):
        return str(self.__dict__)

    def set_name(self, name):
        self.name = name

    def get_name(self):
        return self.name

    def set_id(self, id):
        self.id = id

    def get_id(self):
        return self.id

    def set_created_at(self, date):
        self.created_at = str(date)

    def get_created_at(self):
        return self.created_at

    def check():
        pass


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

    def get_url_by_id(self, id):
        conn = self.connect()
        with conn.cursor() as curs:
            curs.execute(
                'SELECT name, created_at FROM urls WHERE id=%s',
                (id,))
            url_data = curs.fetchall()
        conn.close()
        name, created_at = url_data[0]
        return Url(name, id, str(created_at))

    def get_urls(self):
        conn = self.connect()
        with conn.cursor() as curs:
            curs.execute('SELECT * FROM urls')
            db_data = curs.fetchall()
        conn.close()
        db_data.reverse()
        urls = [Url(name, id, created_at) for id, name, created_at in db_data]
        return urls
