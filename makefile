test:
	pytest -x --ignore=tests/app -p no:warnings orwynn

lint:
	flake8 \
		--exclude .git,__pycache__,docs/source/conf.py,old,build,dist,.venv
