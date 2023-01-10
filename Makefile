test:
	poetry run coverage run -m pytest -x -v --ignore=tests/app -p no:warnings orwynn tests

lint:
# Ignore:
#		- W503:
#				Obsolete. Line breaks should occure before binary operator according to
#				PEP8.  See https://www.flake8rules.com/rules/W503.html
#		- E999:
#				Doesn't recognize new "match" syntax.
#		- B008:
#				Do not restrict calling functions in defaults (fastapi requirement).
#		- EM101:
#				Why is it bad to pass string literal directly to exception raised?
#
# Main package __init__.py shouldn't be lintered since it may contain unused
# imports.
	poetry run ruff \
		--select=ALL \
		--fix \
		--ignore=E999,D,ANN,PT,ARG,B008,EM101,FBT \
		--line-length=79 \
		--isolated \
		--max-complexity 10 \
		--per-file-ignores="__init__.py:F401,*_test.py:S101,conftest.py:F401" \
		--exclude .git,__pycache__,docs/source/conf.py,old,build,dist,.venv,.pytest_cache,.vscode \
		.

check: lint test

coverage:
	poetry run coverage report -m

coverage-html:
	poetry run coverage html --show-contexts && python -m http.server -d htmlcov 8000

dev:
	poetry run uvicorn orwynn:app --reload
