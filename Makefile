.PHONY: clean clean-test clean-pyc clean-build docs help
.DEFAULT_GOAL := help
define BROWSER_PYSCRIPT
import os, webbrowser, sys
try:
	from urllib import pathname2url
except:
	from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT
BROWSER := python -c "$$BROWSER_PYSCRIPT"

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-build clean-pyc clean-test clean-machine-objects ## remove all build, test, coverage and Python artifacts


clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/

clean-machine-objects:
	find ariane/locale -name '*.mo' -delete

lint: ## check style with flake8
	flake8 ariane tests

test: ## run tests quickly with the default Python
	py.test

test-all: ## run tests on every Python version with tox
	tox

coverage: ## check code coverage quickly with the default Python
	coverage run --source ariane -m pytest
	coverage report -m
	coverage html
	$(BROWSER) htmlcov/index.html

portable-objects:
	find ariane/ -iname "*.py" | xargs xgettext --keyword=_ --language=Python --add-comments --sort-output -o ariane/locale/ariane.pot --from-code=utf-8
	msgmerge --output-file=ariane/locale/en_US/LC_MESSAGES/ariane.po ariane/locale/en_US/LC_MESSAGES/ariane.po ariane/locale/ariane.pot
	msgmerge --output-file=ariane/locale/de_DE/LC_MESSAGES/ariane.po ariane/locale/de_DE/LC_MESSAGES/ariane.po ariane/locale/ariane.pot

tx-push:
	tx push --source

tx-pull:
	tx pull

machine-objects:
	msgfmt --output-file=ariane/locale/en_US/LC_MESSAGES/ariane.mo ariane/locale/en_US/LC_MESSAGES/ariane.po
	msgfmt --output-file=ariane/locale/de_DE/LC_MESSAGES/ariane.mo ariane/locale/de_DE/LC_MESSAGES/ariane.po

docs: ## generate Sphinx HTML documentation, including API docs
	rm -f docs/ariane.rst
	rm -f docs/modules.rst
	sphinx-apidoc -o docs/ ariane
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	$(BROWSER) docs/_build/html/index.html

servedocs: docs ## compile the docs watching for changes
	watchmedo shell-command -p '*.rst' -c '$(MAKE) -C docs html' -R -D .

release: clean ## package and upload a release
	python setup.py sdist upload
	python setup.py bdist_wheel upload

dist: clean ## builds source and wheel package
	python setup.py sdist
	python setup.py bdist_wheel
	ls -l dist

install: clean ## install the package to the active Python's site-packages
	pip install .

install-dev: clean ## install the package and all packages to develop
	pip install --editable .[test]

install-en:
	python -m spacy download en

install-de:
	python -m spacy download de

install-all-languages: install-de install-en

install-all: install-dev install-all-languages
