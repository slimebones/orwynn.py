set shell := ["nu", "-c"]

test target="" show="all" *flags="":
	poetry run coverage run -m pytest -x --ignore=tests/app -p no:warnings --show-capture={{show}} --failed-first --asyncio-mode=auto {{flags}} tests/{{target}}

lint target="." *flags="":
	poetry run ruff {{flags}} {{target}}

check: lint test

coverage:
	poetry run coverage report -m

coverage_html:
	poetry run coverage html --show-contexts; python -m http.server -d htmlcov 8000

serve_doc:
	poetry run mkdocs serve -a localhost:3100 -w .

build_doc:
	poetry run mkdocs build

serve_native_doc:
	python3 -m http.server -d site 3100

build_docker_doc: build_doc
	docker-compose -f docker-compose.docs.yml up -d --build --remove-orphans

up_docker_doc:
	docker-compose -f docker-compose.docs.yml up -d

down_docker_doc:
	docker-compose -f docker-compose.docs.yml down

