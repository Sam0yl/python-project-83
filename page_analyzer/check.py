class Check():
    def __init__(self, url_id='', created_at='', data={}):
        DEFAULT_VALUES = {
            'id': '',
            'url_id': url_id,
            'status_code': '',
            'h1': '',
            'title': '',
            'description': '',
            'created_at': str(created_at)
            }

        sorted_data = {key: value if value is not None else ''
                       for key, value in data.items()}

        values = {**DEFAULT_VALUES, **sorted_data}

        self.url_id = values['url_id']
        self.created_at = str(values['created_at'])
        self.id = values['id']
        self.code = values['status_code']
        self.title = values['title']
        self.h1 = values['h1']
        self.description = values['description']

    def __str__(self):
        return str(self.__dict__)
