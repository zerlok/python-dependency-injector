ifneq ($(wildcard .venv/*),)
PROJECT_PYTHON_PATH ?= .venv/bin/
else
PROJECT_PYTHON_PATH ?=
endif

PYTHON ?= $(PROJECT_PYTHON_PATH)python
PIP ?= $(PROJECT_PYTHON_PATH)pip
CYTHON ?= $(PROJECT_PYTHON_PATH)cython
FLAKE8 ?= $(PROJECT_PYTHON_PATH)flake8
MYPY ?= $(PROJECT_PYTHON_PATH)mypy
COVERAGE ?= $(PROJECT_PYTHON_PATH)coverage
PYDOCSTYLE ?= $(PROJECT_PYTHON_PATH)pycodestyle
TWINE ?= $(PROJECT_PYTHON_PATH)twine
SPHINX_AUTOBUILD ?= $(PROJECT_PYTHON_PATH)sphinx-autobuild

VERSION := $(shell python setup.py --version)

CYTHON_SRC := $(shell find src/dependency_injector -name '*.pyx')

CYTHON_DIRECTIVES = -Xlanguage_level=2

ifdef DEPENDENCY_INJECTOR_DEBUG_MODE
	CYTHON_DIRECTIVES += -Xprofile=True
	CYTHON_DIRECTIVES += -Xlinetrace=True
endif


clean:
	# Clean sources
	find src -name '*.py[cod]' -delete
	find src -name '__pycache__' -delete
	find src -name '*.c' -delete
	find src -name '*.h' -delete
	find src -name '*.so' -delete
	find src -name '*.html' -delete
	# Clean tests
	find tests -name '*.py[co]' -delete
	find tests -name '__pycache__' -delete
	# Clean examples
	find examples -name '*.py[co]' -delete
	find examples -name '__pycache__' -delete

cythonize:
	# Compile Cython to C
	$(CYTHON) -a $(CYTHON_DIRECTIVES) $(CYTHON_SRC)
	# Move all Cython html reports
	mkdir -p reports/cython/
	find src -name '*.html' -exec mv {}  reports/cython/  \;

build: clean cythonize
	# Compile C extensions
	$(PYTHON) setup.py build_ext --inplace

docs-live:
	$(SPHINX_AUTOBUILD) docs docs/_build/html

install: uninstall clean cythonize
	$(PIP) install -ve .

uninstall:
	- $(PIP) uninstall -y -q dependency-injector 2> /dev/null

test:
	# Unit tests with coverage report
	$(COVERAGE) erase
	$(COVERAGE) run --rcfile=./.coveragerc -m pytest -c tests/.configs/pytest.ini
	$(COVERAGE) report --rcfile=./.coveragerc
	$(COVERAGE) html --rcfile=./.coveragerc

check:
	$(FLAKE8) src/dependency_injector/
	$(FLAKE8) examples/

# TODO: fix pydocstyle run: src/dependency_injector/ext/flask.py:76:80: E501 line too long (84 > 79 characters)
                            #make: Leaving directory '/home/zerlok/dev/zerlok/dependency-injector'
                            #make: *** [/home/zerlok/dev/zerlok/dependency-injector/Makefile:74: check] Error 1
#	$(PYDOCSTYLE) src/dependency_injector/
#	$(PYDOCSTYLE) examples/

	$(MYPY) tests/typing

test-publish: cythonize
	# Create distributions
	$(PYTHON) setup.py sdist
	# Upload distributions to PyPI
	$(TWINE) upload --repository testpypi dist/dependency-injector-$(VERSION)*

publish:
	# Merge release to master branch
	git checkout master
	git merge --no-ff release/$(VERSION) -m "Merge branch 'release/$(VERSION)' into master"
	git push origin master
	# Create and upload tag
	git tag -a $(VERSION) -m 'version $(VERSION)'
	git push --tags
