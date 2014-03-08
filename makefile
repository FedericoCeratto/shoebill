# vim: set noexpandtab:

PROJ = shoebill
VERSION=$(python setup.py --version)

# Default unit testing globbing
TESTGLOB = test*.py

all: help

help:
	egrep "^# target:" [Mm]akefile | cut -c11-

# target: cleanbuild - Remove build dir
cleanbuild:
	python setup.py clean
	find . -name '*.pyc' -delete

# target: build - build Python package
build: cleanbuild
	python setup.py sdist
	python setup.py bdist

prepare-cover-dir:
	# If there isn't a cover symlink, create and link the directory
	test -s cover || (mkdir -p docs/_build/html/cover && ln -s docs/_build/html/cover)
	rm -rf cover/*

# target: coverage - Run unit testing + code coverage
coverage: prepare-cover-dir
	nosetests tests/$(TESTGLOB) --with-coverage --cover-erase --cover-package=$(PROJ) --cover-html

# target: coverage-base - Run base functional testing + code coverage
coverage-base: TESTGLOB=test.py
coverage-base: coverage

# target: pylint - run pylint
pylint:
	pylint $(PROJ) tests

# target: doc - Build sphinx docs
doc:
	#cd docs && sphinx-build -b html .  _build/html
	sphinx-build -b html docs  docs/_build/html

# target: docwithcoverage - Build sphinx docs
docwithcoverage: coverage doc

cover-html:
	nosetests --with-coverage --cover-package $(PROJ)  --cover-html

cover-basic-loop:
	while true;do inotifywait */*.py;nosetests tests/test_basic.py --with-coverage --cover-package=shoebill --cover-erase;sleep 1;done

cover-functional-loop:
	while true;do inotifywait */*.py;nosetests tests/test_functional.py --with-coverage --cover-package=shoebill --cover-erase;sleep 1;done

cover-loop:
	while true;do inotifywait */*.py;nosetests tests/test*.py --with-coverage --cover-package=shoebill --cover-erase;sleep 1;done

