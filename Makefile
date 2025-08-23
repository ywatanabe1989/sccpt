# Makefile for sccpt package

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
	pip install -e .

test:
	python test_sccpt.py

build: clean
	python setup.py sdist bdist_wheel

upload-test: build
	python -m twine upload --repository testpypi dist/*

upload: build
	@echo "⚠️  This will upload to PyPI. Continue? [y/N]"
	@read ans && [ $${ans} = y ]
	python -m twine upload dist/*

clean:
	rm -rf build dist *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete