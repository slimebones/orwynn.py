test:
	poetry run coverage run -m pytest -x -v --ignore=tests/app -p no:warnings tests --show-capture=all --failed-first orwynn

lint:
# Ignore:
#		- W503:
#				Obsolete. Line breaks should occure before binary operator according to
#				PEP8.  See https://www.flake8rules.com/rules/W503.html
#		- E999:
#				Doesn't recognize new "match" syntax.
#		- B008:
#				Do not restrict calling functions in defaults (fastapi requirement).
#		- EM101,EM102:
#				Why is it bad to pass string literal directly to exception raised?
#		- N*:
#				Passing PascalCase names is allowed.
#		- A*:
#				Builtin shadowing is allowed in local contexts.
#		- RET504:
#				Sometimes it's typehinting-wise to declare variable and assign it
#				in different logical branches before returning.
#		- RET505,RET506:
#				Not clear why first branch of if-elif-else should not contain raise
#				statement.
#		- RET507:
#				It's ok to have "continue" and then "else: raise...".
#		- Q003:
#				Escaping inner quotes to not change outer ones is OK.
#		- ISC002,ISC003:
#				No strict rules for string concatenation.
#		- PGH003:
#				To not search for specific error code on type ignoring.
#		- RUF001:
#				Do not replace symbols in false-positive scenario.
#
# Main package __init__.py shouldn't be lintered since it may contain unused
# imports.
	poetry run ruff \
		--select=ALL \
		--fix \
		--ignore=E999,D,ANN,PT,ARG,B008,EM101,EM102,FBT,N,RET504,RET505,RET506,RET507,Q003,ISC002,ISC003,A,PGH003,RUF001 \
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
