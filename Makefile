.PHONY: run test lint format check

run:
	venv/bin/python manage.py runserver

test:
	venv/bin/pytest --cov=apps

lint:
	venv/bin/flake8 apps config bot tests

format:
	venv/bin/black apps config bot tests manage.py
	venv/bin/isort apps config bot tests manage.py

check: lint
	venv/bin/black --check apps config bot tests manage.py
	venv/bin/isort --check-only apps config bot tests manage.py
	venv/bin/pytest -q
