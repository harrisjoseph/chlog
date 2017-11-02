.PHONY: test upload clean bootstrap build venv

test:
	sh -c '. venv/bin/activate; nosetests tests'

test-all:
	tox

build: test-all
	python setup.py sdist bdist_wheel

upload: build test-all
	twine upload -r pypi dist/*
	make clean
	
register:
	python setup.py register

clean:
	rm -f MANIFEST
	rm -rf build dist *.egg-info
	
bootstrap: venv
	venv/bin/pip install -e .
	make clean

venv: 
	virtualenv --python=python3 venv
	venv/bin/pip install --upgrade pip
	venv/bin/pip install --upgrade setuptools
