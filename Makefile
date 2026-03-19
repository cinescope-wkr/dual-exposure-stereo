.PHONY: docs-install docs-serve docs-build

docs-install:
	pip install -r requirements-docs.txt

docs-serve:
	mkdocs serve -a 0.0.0.0:8000

docs-build:
	mkdocs build --strict
