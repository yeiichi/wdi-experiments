Quickstart
==========

Python API
----------

Import the package and request recent WDI values with an ISO 3166 alpha-3
country code:

.. code-block:: python

   from wdi_experiments.main import get_population_data

   result = get_population_data("JPN", years=5)
   print(result["indicator_name"])
   print(result["years"])

The result is a JSON-serializable dictionary:

.. code-block:: python

   {
       "country": "JPN",
       "source": "World Bank World Development Indicators",
       "indicator": "SP.POP.TOTL",
       "indicator_name": "Population, total",
       "unit": "persons",
       "years": [
           {"year": 2021, "population": 125681593},
           {"year": 2022, "population": 125124989},
       ],
   }

Available indicators:

``get_population_data(country, years=10)``
   WDI ``SP.POP.TOTL``: population, total.

``get_gdp_data(country, years=10)``
   WDI ``NY.GDP.MKTP.CD``: GDP in current US dollars.

``get_gdp_per_capita_data(country, years=10)``
   WDI ``NY.GDP.PCAP.CD``: GDP per capita in current US dollars.

For dashboards or batch work, use the corresponding ``*_many`` functions to
fetch several countries with one World Bank API request:

.. code-block:: python

   from wdi_experiments.main import get_gdp_data_many

   data = get_gdp_data_many(["JPN", "USA", "IND"], years=10)
   print(data["USA"]["years"])

Command Line
------------

The CLI prints JSON for one country and one indicator:

.. code-block:: bash

   uv run wdi-experiments population JPN --years 10
   uv run wdi-experiments gdp USA --years 5
   uv run wdi-experiments gdp-per-capita IND --years 20

Country codes are normalized to uppercase, but they must be valid three-letter
ISO 3166 alpha-3 codes such as ``JPN``, ``USA``, or ``IND``.
