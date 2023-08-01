import datetime
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from page_analyzer.check import CheckData


class Url():
    def __init__(self, url, id='', created_at=''):
        self.url_code = urlparse(url)
        self.name = f'{self.url_code.scheme}://{self.url_code.netloc}'
        self.id = id
        self.created_at = created_at
        self.last_check = ''

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

    def run_check(self):
        date = datetime.date.today()
        try:
            response = requests.get(self.name)
        except Exception:
            return None
        html = BeautifulSoup(response.text, "html.parser")
        meta_tag = html.find(
            'meta', attrs={'name': 'description', 'content': True})
        data = {
            'status_code': response.status_code,
            'title': '' if html.title is None else html.title.string,
            'h1': '' if html.h1 is None else html.h1.string,
            'description': '' if meta_tag is None else meta_tag['content']
        }

        self.last_check = CheckData(self.id, date, data)
        return self.last_check

    def set_last_check(self, check):
        self.last_check = check
