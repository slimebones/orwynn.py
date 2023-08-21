# Getting Started

As soon as you've [installed](index.md#installation) Orwynn, you may need to generate a new app-project. This can be done using the [Generate CLI](GenerateCLI.md):
```bash
orwynn generate app myapp
```

Which will generate all starter application files in directory `./myapp`.

By default, only base files are created:
```
.
├── .venv
├── src/
│   ├── __init__.py
│   └── main.py
├── .gitignore
├── apprc.yml
├── conftest.py
├── Makefile
├── poetry.lock
└── pyproject.toml
```
see [Generate CLI](GenerateCLI.md#new-project-generation) for details on features you can include on a new project generation.

Brief overview of files and directories generated:

|  |  |
| --- | --- |
| `.venv` | Virtual environment files with installed dependencies. |
| `src/__init__.py` | Empty file for proper Python packaging. |
| `src/main.py` | Main application entrypoint containing setup methods and example modules. |
| `.gitignore` | List of files ignored by Git. |
| `apprc.yml` | [Orwynn Configuration File](AppRC.md). |
| `conftest.py` | Configuration for [Pytest](https://docs.pytest.org/en/7.4.x/) testing. |
| `Makefile` | [GNU Makefile](https://www.gnu.org/software/make/manual/html_node/Simple-Makefile.html) for hosting the project's commands. |
| `poetry.lock` | [Poetry](https://python-poetry.org/) locked dependencies. |
| `pyproject.toml` | [Modern Python package informational file](https://pip.pypa.io/en/stable/reference/build-system/pyproject-toml/). |

After the generation, the application can be started using a command:
```bash
cd myapp
make serve mode=dev
```

This will serve the created application at `http://localhost:3000` in DEV [App Mode](AppMode.md).
