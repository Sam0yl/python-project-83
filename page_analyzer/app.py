from flask import Flask, render_template, request, \
    redirect, url_for, flash, get_flashed_messages
from page_analyzer.data import UrlRepository, Url
from page_analyzer.validator import validate_url


app = Flask(__name__)

app.secret_key = "secret_key"
# необходима доработка секретного ключа через dotenv и переменную окружения
# app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


repo = UrlRepository()


@app.get('/')
def main_page():
    url = ''
    errors = {}
    return render_template(
        'index.html',
        errors=errors,
        url=url
        )


@app.post('/urls')
def add_url():
    requested_url = request.form.to_dict()['url']
    url = Url(requested_url)
    errors = validate_url(url.name)
    if errors:
        return render_template(
            'index.html',
            errors=errors,
            url=url.name
            ), 422
    if not repo.is_url_in_repository(url):
        repo.add_url(url)
        repo.assign_url_id(url)
        flash('Страница успешно добавлена', 'alert-success')
        return redirect(
            url_for('get_url', id=url.id)
            )
    repo.assign_url_id(url)
    flash('Страница уже существует', 'alert-info')
    return redirect(
        url_for('get_url', id=url.id)
        )


@app.get('/urls')
def read_urls():
    urls = repo.get_urls()
    return render_template(
        'urls.html', urls=urls
        )


@app.get('/urls/<id>')
def get_url(id):
    messages = get_flashed_messages(with_categories=True)
    url = repo.get_url_by_id(id)
    return render_template(
            'url.html',
            messages=messages,
            url=url
            )
