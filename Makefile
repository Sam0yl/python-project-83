install:
	poetry install

test:
	poetry run pytest

test-coverage:
	poetry run pytest --cov=app --cov-report xml

publish:
	poetry publish --dry-run

package-install:
	python3 -m pip install --user dist/*.whl

lint:
	poetry run flake8 ./page_analyzer

selfcheck:
	poetry check

check: selfcheck test lint

setup: install build package-install

dev:
	poetry run flask --app page_analyzer:app --debug run

PORT ?= 8000
start:
	poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app