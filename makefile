test:
	pytest -x --ignore=tests/app -p no:warnings orwynn tests

lint:
# Ignore:
#		- W503:
#				Obsolete. Line breaks should occure before binary operator according to
#				PEP8.  See https://www.flake8rules.com/rules/W503.html
#
# Main package __init__.py shouldn't be lintered since it may contain unused
# imports.
	flake8 \
		--count \
		--max-line-length=79 \
		--disable-noqa \
		--ignore=W503 \
		--isolated \
		--exclude .git,__pycache__,docs/source/conf.py,old,build,dist,.venv,.pytest_cache,.vscode,orwynn/__init__.py \
		--max-complexity 10

check: test lint
