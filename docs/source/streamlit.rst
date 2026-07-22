Streamlit App
=============

``wdi-experiments`` includes a public-facing Streamlit app at
``apps/streamlit/lab.py``. The app is called **WDI Explorer** and is intended
mainly for checking that the package, data fetching, and visualization flow are
working end to end.

The GUI displays a disclaimer that it is for experimental purposes. For serious
research, citation, bulk downloads, metadata review, and more complete
indicator discovery, use the official `World Development Indicators DataBank
<https://databank.worldbank.org/source/world-development-indicators>`_.

Run Locally
-----------

Start the app from the repository root:

.. code-block:: bash

   uv sync
   uv run streamlit run apps/streamlit/lab.py

The root directory matters because the app imports the local package from
``src/`` and writes its local cache under ``.cache/streamlit-wdi/data.json``.

What the App Does
-----------------

The app fetches data from the World Bank WDI API through the local
``wdi_experiments`` package.

The app provides:

Indicator selection
   Choose population, GDP, or GDP per capita.

Country comparison
   Select one or more countries from the curated country list.

Year window
   Request from 1 to 60 recent years.

Interactive chart
   View an Altair line chart with country colors, yearly points, and tooltips.

Data table
   Expand the data section to inspect the fetched values.

References
   Expand the references section for links to the official WDI DataBank and
   World Bank API documentation.

Caching
-------

The app uses two cache layers:

``st.cache_data``
   Keeps repeated selections fast during an app session.

Disk cache
   Stores fetched results in ``.cache/streamlit-wdi/data.json`` for up to one
   month. Missing countries are fetched without refetching the whole selection.

The cache contains World Bank API responses only. It does not store user
accounts, secrets, or uploaded files.

Public Deployment
-----------------

For Streamlit Community Cloud, use this app entrypoint:

.. code-block:: text

   apps/streamlit/lab.py

Streamlit Community Cloud runs ``streamlit run`` from the repository root, so
the same path behavior used locally applies in production. The official
Streamlit documentation also notes that dependency files can live at the
repository root or beside the entrypoint file, and that ``uv.lock`` is one of
the recognized dependency files.

Before publishing the repository, verify:

* The GitHub repository is public or connected to the Streamlit workspace.
* The selected branch contains ``apps/streamlit/lab.py``, ``src/``,
  ``pyproject.toml``, and ``uv.lock``.
* The deployment uses Python 3.11 or newer.
* No secrets are required for the current World Bank API integration.

References:

* `World Development Indicators DataBank <https://databank.worldbank.org/source/world-development-indicators>`_
* `World Bank API developer information <https://datahelpdesk.worldbank.org/knowledgebase/topics/125589-developer-information>`_
* `Streamlit Community Cloud file organization <https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/file-organization>`_
* `Streamlit Community Cloud app dependencies <https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies>`_
