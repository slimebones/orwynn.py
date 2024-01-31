export pytest_show=all
export args
export t

testapp.serve:
	cd tests/app && $(MAKE) dev

test:
	poetry run coverage run -m pytest -x --ignore=tests/app -p no:warnings --show-capture=$(pytest_show) --failed-first $(args) tests/$(t)

lint:
	poetry run ruff $(args) $(t)

check: lint test

coverage:
	poetry run coverage report -m

coverage.html:
	poetry run coverage html --show-contexts && python -m http.server -d htmlcov 8000

docs.serve:
	poetry run mkdocs serve -a localhost:3100 -w $(t)

docs.build:
	poetry run mkdocs build

docs.serve-native:
	python3 -m http.server -d site 3100

docs.build-docker: docs.build
	docker-compose -f docker-compose.docs.yml up -d --build --remove-orphans

docs.up-docker:
	docker-compose -f docker-compose.docs.yml up -d

docs.down-docker:
	docker-compose -f docker-compose.docs.yml down
