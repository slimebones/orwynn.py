export PYTEST_SHOW=all

testapp.serve:
	cd tests/app && $(MAKE) dev

test:
	poetry run coverage run -m pytest -x --ignore=tests/app -p no:warnings --show-capture=$(PYTEST_SHOW) --failed-first orwynn tests

lint:
	poetry run ruff .

check: lint test

coverage:
	poetry run coverage report -m

coverage.html:
	poetry run coverage html --show-contexts && python -m http.server -d htmlcov 8000

docs.serve:
	poetry run mkdocs serve -a localhost:3100 -w orwynn

docs.build:
	poetry run mkdocs build

docs.serve_native:
	python3 -m http.server -d site 3100

docs.docker.build: docs.build
	docker-compose -f docker-compose.docs.yml up -d --build --remove-orphans

docs.docker.up:
	docker-compose -f docker-compose.docs.yml up -d

docs.docker.down:
	docker-compose -f docker-compose.docs.yml down
