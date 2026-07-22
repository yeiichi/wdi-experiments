Development
===========

Common Commands
---------------

Install dependencies and run checks locally:

.. code-block:: bash

   uv sync
   uv run ruff check .
   uv run pytest

Build the docs:

.. code-block:: bash

   uv run sphinx-build -b html docs/source docs/build/html

Run the app:

.. code-block:: bash

   uv run streamlit run apps/streamlit/lab.py

Project Layout
--------------

``src/wdi_experiments/``
   Package code, including API functions, CLI wiring, indicator selection, and
   the World Bank HTTP client.

``apps/streamlit/lab.py``
   Streamlit WDI Explorer app.

``tests/``
   Unit tests for indicator parsing, grouping, input validation, and CLI
   behavior.

``docs/source/``
   Sphinx documentation source.

Testing Strategy
----------------

Tests avoid live World Bank requests by monkeypatching the fetch layer. This
keeps the suite fast and repeatable while still checking parsing, sorting,
batch grouping, and error handling.

Documentation Workflow
----------------------

Update the Sphinx pages whenever behavior changes in one of the user-facing
surfaces: Python API, CLI, or Streamlit app. Before publishing, run the docs
build and inspect warnings:

.. code-block:: bash

   uv run sphinx-build -b html docs/source docs/build/html

Public App Checklist
--------------------

Because this repository is intended to be published with a Streamlit Community
Cloud app, review the following before release:

* The Streamlit entrypoint remains ``apps/streamlit/lab.py``.
* Public docs avoid private paths, tokens, or unpublished operational notes.
* Runtime behavior does not require secrets.
* The branch selected in Streamlit contains ``src/``, ``pyproject.toml``, and
  ``uv.lock``.
