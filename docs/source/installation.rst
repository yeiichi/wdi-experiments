Installation
============

Requirements
------------

``wdi-experiments`` requires Python 3.11 or newer. The repository is managed
with `uv <https://docs.astral.sh/uv/>`_, which installs the package, the test
tooling, Sphinx, and the Streamlit app dependencies from ``pyproject.toml`` and
``uv.lock``.

Install the project for local use:

.. code-block:: bash

   uv sync

Run the command-line entrypoint:

.. code-block:: bash

   uv run wdi-experiments --help

Run the Streamlit app from the repository root:

.. code-block:: bash

   uv run streamlit run apps/streamlit/lab.py

Dependency Notes
----------------

The core package uses the Python standard library to call the World Bank API.
The interactive app and documentation tooling are development dependencies:

``streamlit``
   Hosts the WDI Explorer UI.

``pandas`` and ``altair``
   Used by Streamlit and the app to shape tabular data and render charts.

``sphinx`` and ``furo``
   Build this documentation.

When deploying publicly, keep the dependency declaration in the repository so
the hosting service can reproduce the same environment.
