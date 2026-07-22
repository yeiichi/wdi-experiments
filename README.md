# wdi-experiments

A Python package.

Layers: cli, streamlit, docs, container, github, oss

## Installation

```bash
uv sync
```

## Usage

```python
import wdi_experiments

print(wdi_experiments.__version__)
```

## Development

```bash
uv sync
uv run ruff check .
uv run pytest
```

## Command-Line Application

```bash
uv run wdi-experiments --help
```

## Streamlit Laboratory

```bash
uv run streamlit run apps/streamlit/lab.py
```

## Documentation

```bash
uv run sphinx-build -b html docs/source docs/build/html
```

## Container

```bash
docker build -t wdi-experiments .
```

## GitHub Automation

CI and release workflow templates are available in `.github/workflows/`.

## Open-Source Publication

This project includes a `LICENSE`, `CHANGELOG.md`, and Read the Docs configuration starter. Use this with the `docs` layer when publishing documentation.
