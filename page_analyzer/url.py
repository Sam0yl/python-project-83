import datetime
import requests
import validators
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from page_analyzer.check import CheckData


def set_name(url):
    if not validators.url(url):
        name = url
    else:
        url_code = urlparse(url)
        name = f'{url_code.scheme}://{url_code.netloc}'
    return name


class Url():
    def __init__(self, url, id='', created_at=''):
        self.name = set_name(url)
        self.id = id
        self.created_at = created_at
        self.last_check = ''

    def __str__(self):
        return str(self.__dict__)

    def run_check(self):
        date = datetime.date.today()
        try:
            response = requests.get(self.name)
            response.raise_for_status()
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
