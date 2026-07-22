wdi-experiments documentation
=============================

``wdi-experiments`` is a small Python project for exploring World Bank
World Development Indicators (WDI) data from code, the command line, and a
Streamlit app.

The current package focuses on recent country-level values for population,
GDP, and GDP per capita. It normalizes ISO 3166 alpha-3 country codes, fetches
JSON data from the World Bank API, and returns compact dictionaries that are
easy to serialize or chart.

The package and app fetch data from the World Bank WDI API. For technical API
details, see the `World Bank developer information
<https://datahelpdesk.worldbank.org/knowledgebase/topics/125589-developer-information>`_.
For serious research workflows, use the official `World Development Indicators
DataBank <https://databank.worldbank.org/source/world-development-indicators>`_.

Main Surfaces
-------------

Python API
   Use ``wdi_experiments`` from notebooks, scripts, or tests.

Command line
   Fetch one indicator for one ISO3 country and print JSON.

Streamlit Explorer
   Compare one indicator across multiple countries with an interactive chart
   and table.

Quick Commands
--------------

.. code-block:: bash

   uv sync
   uv run wdi-experiments population JPN --years 10
   uv run streamlit run apps/streamlit/lab.py

For local development and documentation checks:

.. code-block:: bash

   uv sync
   uv run pytest
   uv run ruff check .
   uv run sphinx-build -b html docs/source docs/build/html

Contents
--------

.. toctree::
   :maxdepth: 2

   installation
   quickstart
   streamlit
   api
   development
