# Makefile for cam package

# Use Python from virtual environment if activated, otherwise use python3
ifdef VIRTUAL_ENV
    PYTHON := $(VIRTUAL_ENV)/bin/python
    PIP := $(VIRTUAL_ENV)/bin/pip
else
    PYTHON := python3
    PIP := pip3
endif

.PHONY: help install test build upload upload-test clean

help:
	@echo "Available commands:"
	@echo "  make install      Install package in development mode"
	@echo "  make test         Run tests"
	@echo "  make build        Build distribution packages"
	@echo "  make upload-test  Upload to TestPyPI"
	@echo "  make upload       Upload to PyPI (requires ~/.pypirc)"
	@echo "  make clean        Remove build artifacts"

install:
	$(PIP) install -e .

test:
	$(PYTHON) -m pytest tests/

build: clean
	$(PYTHON) setup.py sdist bdist_wheel

upload-test: build
	$(PYTHON) -m twine upload --repository testpypi dist/*

upload: build
	@echo "⚠️  This will upload to PyPI. Continue? [y/N]"
	@read ans && [ $${ans} = y ]
	$(PYTHON) -m twine upload dist/*

clean:
	rm -rf build dist *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete