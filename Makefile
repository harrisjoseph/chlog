.PHONY: test upload clean bootstrap build venv

test:
	sh -c '. venv/bin/activate; nosetests tests'

test-all:
	tox

build: test-all
	python setup.py sdist bdist_wheel

upload: build test-all
	twine upload -r nexus dist/*
	make clean
	
clean:
	rm -f MANIFEST
	rm -rf build dist *.egg-info
	
bootstrap: venv
	venv/bin/python setup.py develop
	make clean

venv: 
	virtualenv --python=python3 venv
	venv/bin/pip install --upgrade pip
	venv/bin/pip install --upgrade setuptools
