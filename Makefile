install:
	poetry install

test:
	poetry run pytest

test-coverage:
	poetry run pytest --cov=app --cov-report xml

lint:
	poetry run flake8 ./page_analyzer

dev:
	poetry run flask --app page_analyzer:app --debug run

PORT ?= 8000
start:
	poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app