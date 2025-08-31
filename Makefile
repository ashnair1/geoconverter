# Makefile for geoconverter development

.PHONY: help install install-dev test test-verbose lint format type-check clean build upload-test upload docs-serve docs-build pre-commit setup-dev

help:				## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:			## Install package in current environment
	pip install -e .

install-dev:		## Install package in development mode with all dependencies
	pip install -e ".[dev]"
	pre-commit install

setup-dev:			## Set up complete development environment
	conda create -n geoconverter-dev python=3.11 gdal numpy -y || true
	conda activate geoconverter-dev && make install-dev

test:				## Run tests
	pytest

test-verbose:		## Run tests with verbose output and coverage
	pytest -v --cov=geoconverter --cov-report=term-missing --cov-report=html

test-integration:	## Run integration tests only
	pytest -v -m integration

lint:				## Run linting with ruff
	ruff check geoconverter tests scripts

format:				## Format code with ruff
	ruff format geoconverter tests scripts
	ruff check geoconverter tests scripts --fix

type-check:			## Run type checking with mypy
	mypy geoconverter

pre-commit:			## Run all pre-commit hooks
	pre-commit run --all-files

clean:				## Clean build artifacts and cache files
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

build:				## Build package
	python -m build

upload-test:		## Upload to TestPyPI
	python -m twine upload --repository testpypi dist/*

upload:				## Upload to PyPI
	python -m twine upload dist/*

docs-serve:			## Serve documentation locally
	mkdocs serve

docs-build:			## Build documentation
	mkdocs build

# GDAL compatibility testing
test-gdal:			## Test GDAL compatibility across versions
	./scripts/test_gdal_compatibility.sh

monitor-gdal:		## Check for new GDAL releases
	python scripts/monitor_gdal.py

# Cesium terrain builder tasks
build-ctb:			## Build cesium-terrain-builder
	cd cesium-terrain-builder && \
	mkdir -p build && \
	cd build && \
	cmake .. -DCMAKE_BUILD_TYPE=Release \
		-DGDAL_LIBRARY_DIR=$$CONDA_PREFIX/lib \
		-DGDAL_LIBRARY=$$CONDA_PREFIX/lib/libgdal.so \
		-DGDAL_INCLUDE_DIR=$$CONDA_PREFIX/include \
		-DZLIB_LIBRARY=$$CONDA_PREFIX/lib/libz.so \
		-DZLIB_INCLUDE_DIR=$$CONDA_PREFIX/include && \
	cmake --build . --config Release -j$$(nproc)

clean-ctb:			## Clean cesium-terrain-builder build
	rm -rf cesium-terrain-builder/build*

# Quality checks
check: lint type-check test  ## Run all quality checks

# Release workflow
release-check:		## Check if ready for release
	@echo "Running pre-release checks..."
	@make clean
	@make install-dev
	@make check
	@make build
	@echo "✅ Ready for release!"

# Docker testing
docker-test:		## Test with Docker
	docker build -f docker/Dockerfile.gdal-test --build-arg GDAL_VERSION=3.11 -t geoconverter:test .
	docker run --rm geoconverter:test