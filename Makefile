.PHONY: help sync lint test build clean cli app docs docker-build

help:
	@printf "Targets:\n"
	@printf "  sync   Install dependencies with uv\n"
	@printf "  lint   Run ruff checks\n"
	@printf "  test   Run tests\n"
	@printf "  build  Build package artifacts\n"
	@printf "  clean  Remove build and cache artifacts\n"
	@printf "  cli    Run the command-line application\n"
	@printf "  app    Run the Streamlit laboratory\n"
	@printf "  docs   Build documentation\n"
	@printf "  docker-build  Build the container image\n"

sync:
	uv sync

lint:
	uv run ruff check .

test:
	uv run pytest

build:
	uv build

cli:
	uv run wdi-experiments --help

app:
	uv run streamlit run apps/streamlit/lab.py

docs:
	uv run sphinx-build -b html docs/source docs/build/html

docker-build:
	docker build -t wdi-experiments .

clean:
	rm -rf build dist *.egg-info .pytest_cache .ruff_cache
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
