export PYTEST_SHOW=all

testapp.dev:
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

changelog:
# Conventional Commits is used since we use exclamation marks to sign breaking
# commits.
	poetry run git-changelog -c conventional -o CHANGELOG.md .

docs.serve:
	poetry run mkdocs serve -a localhost:9000 -w orwynn

docs.build:
	poetry run mkdocs build
