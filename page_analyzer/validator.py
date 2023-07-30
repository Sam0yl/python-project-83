import validators


def validate_url(url):
    errors = {}
    if not validators.url(url):
        errors['not_valid'] = 'Некорректный URL'
    if not url:
        errors['empty'] = 'URL обязателен'
    return errors
