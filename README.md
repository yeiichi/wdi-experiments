# wdi-experiments

Experiments for fetching and visualizing World Bank World Development
Indicators (WDI) from Python, the command line, and Streamlit.

The current project supports recent country-level population, GDP, and GDP per
capita data. It includes a small Python API, a JSON-printing CLI, Sphinx
documentation, and a Streamlit WDI Explorer intended for public deployment on
Streamlit Community Cloud.

The package and apps fetch data from the World Bank WDI API. The Streamlit app
is for experimental purposes. For serious research, citation, bulk downloads,
or metadata review, use the official [World Development Indicators DataBank](https://databank.worldbank.org/source/world-development-indicators).
For API details, see the [World Bank API developer information](https://datahelpdesk.worldbank.org/knowledgebase/topics/125589-developer-information).

## Installation

```bash
uv sync
```

## Usage

```python
from wdi_experiments.main import get_population_data

result = get_population_data("JPN", years=10)
print(result["years"])
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
uv run wdi-experiments population JPN --years 10
```

## Streamlit Laboratory

```bash
uv run streamlit run apps/streamlit/lab.py
```

The GUI is mainly for checking that data fetching and visualization work
end-to-end. It displays an experimental-use disclaimer and links to the
official WDI DataBank and World Bank API documentation.

For Streamlit Community Cloud, use `apps/streamlit/lab.py` as the app
entrypoint. The app runs from the repository root and uses the local package in
`src/`.

## Documentation

```bash
uv run sphinx-build -b html docs/source docs/build/html
```

## Container

```bash
docker build -t wdi-experiments .
docker run --rm -p 8080:8080 wdi-experiments
```

The image runs the Streamlit laboratory by default:

```bash
uv run --no-sync streamlit run apps/streamlit/lab.py
```

The `--no-sync` flag uses the dependencies baked into the image instead of
syncing them again on startup. The container binds Streamlit to `0.0.0.0` and
uses the `PORT` environment variable when present, which is required by Cloud
Run. Locally it defaults to port `8080`.

## GitHub Automation

CI and release workflow templates are available in `.github/workflows/`.

## Open-Source Publication

This project includes a `LICENSE`, `CHANGELOG.md`, and Read the Docs configuration starter. Use this with the `docs` layer when publishing documentation.
