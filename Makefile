test:
	poetry run coverage run -m pytest -x -v --ignore=tests/app -p no:warnings orwynn tests

lint:
# Ignore:
#		- W503:
#				Obsolete. Line breaks should occure before binary operator according to
#				PEP8.  See https://www.flake8rules.com/rules/W503.html
#		- E999:
#				Doesn't recognize new "match" syntax.
#
# Main package __init__.py shouldn't be lintered since it may contain unused
# imports.
	poetry run ruff \
		--fix \
		--ignore=E999 \
		--line-length=79 \
		--isolated \
		--max-complexity 10 \
		--per-file-ignores="__init__.py:F401" \
		--exclude .git,__pycache__,docs/source/conf.py,old,build,dist,.venv,.pytest_cache,.vscode,conftest.py \
		.

check: lint test

coverage:
	poetry run coverage report -m

coverage-html:
	poetry run coverage html --show-contexts && python -m http.server -d htmlcov 8000

dev:
	poetry run uvicorn orwynn:app --reload
