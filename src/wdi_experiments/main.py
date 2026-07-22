from __future__ import annotations

from wdi_experiments.cli import (
    GdpDataError,
    GdpPerCapitaDataError,
    PopulationDataError,
    get_gdp_data,
    get_gdp_data_many,
    get_gdp_per_capita_data,
    get_gdp_per_capita_data_many,
    get_population_data,
    get_population_data_many,
    main,
)

__all__ = [
    "GdpDataError",
    "GdpPerCapitaDataError",
    "PopulationDataError",
    "get_gdp_data",
    "get_gdp_data_many",
    "get_gdp_per_capita_data",
    "get_gdp_per_capita_data_many",
    "get_population_data",
    "get_population_data_many",
    "main",
]


if __name__ == "__main__":
    raise SystemExit(main())
