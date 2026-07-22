Python API
==========

The indicator API is available from ``wdi_experiments.main`` for convenient
imports:

.. code-block:: python

   from wdi_experiments.main import get_population_data, get_gdp_data

These functions fetch data from the World Bank WDI API. For API parameters,
limits, and technical behavior outside this package, consult the `World Bank
developer information
<https://datahelpdesk.worldbank.org/knowledgebase/topics/125589-developer-information>`_.

Single-Country Functions
------------------------

.. autofunction:: wdi_experiments.main.get_population_data

.. autofunction:: wdi_experiments.main.get_gdp_data

.. autofunction:: wdi_experiments.main.get_gdp_per_capita_data

Batch Functions
---------------

Use batch functions when a chart or report needs several countries. They use
the World Bank API's semicolon-delimited country query format and return a
dictionary keyed by normalized ISO3 code.

.. autofunction:: wdi_experiments.main.get_population_data_many

.. autofunction:: wdi_experiments.main.get_gdp_data_many

.. autofunction:: wdi_experiments.main.get_gdp_per_capita_data_many

Errors
------

The package raises ``ValueError`` for invalid input, such as a non-ISO3 country
code or a non-positive ``years`` value. API, network, timeout, and response
shape problems are raised as indicator-specific aliases of
``WorldBankDataError``:

.. autoclass:: wdi_experiments.main.PopulationDataError

.. autoclass:: wdi_experiments.main.GdpDataError

.. autoclass:: wdi_experiments.main.GdpPerCapitaDataError

Response Shape
--------------

Each successful single-country call returns:

``country``
   Normalized ISO 3166 alpha-3 country code.

``source``
   ``World Bank World Development Indicators``.

``indicator``
   WDI indicator identifier.

``indicator_name``
   Human-readable indicator name.

``unit``
   Value unit, such as ``persons`` or ``current US$``.

``years``
   A list of yearly values sorted from oldest to newest.
