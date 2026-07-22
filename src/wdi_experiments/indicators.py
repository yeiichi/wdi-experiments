from __future__ import annotations

from typing import Any

from wdi_experiments import wdi_client

POPULATION_INDICATOR_ID = "SP.POP.TOTL"
GDP_INDICATOR_ID = "NY.GDP.MKTP.CD"
GDP_PER_CAPITA_INDICATOR_ID = "NY.GDP.PCAP.CD"
DEFAULT_TIMEOUT_SECONDS = wdi_client.DEFAULT_TIMEOUT_SECONDS
PopulationDataError = wdi_client.WorldBankDataError
GdpDataError = wdi_client.WorldBankDataError
GdpPerCapitaDataError = wdi_client.WorldBankDataError


def get_population_data(
    country: str,
    *,
    years: int = 10,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    """Return recent WDI population data for an ISO 3166 alpha-3 country code.

    Population values are returned as people using World Development Indicators
    indicator SP.POP.TOTL, Population, total.
    """

    iso3 = wdi_client.normalize_iso3(country)
    if years <= 0:
        raise ValueError("years must be a positive integer")

    rows = _fetch_population_rows([iso3], years=years, timeout=timeout)
    population = _select_recent_population(rows, years=years)
    if not population:
        raise PopulationDataError(f"No population data returned for {iso3}")

    return {
        "country": iso3,
        "source": "World Bank World Development Indicators",
        "indicator": POPULATION_INDICATOR_ID,
        "indicator_name": "Population, total",
        "unit": "persons",
        "years": population,
    }


def get_population_data_many(
    countries: list[str],
    *,
    years: int = 10,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
) -> dict[str, dict[str, Any]]:
    """Return recent WDI population data for multiple ISO3 country codes.

    The World Bank API supports semicolon-delimited country codes, so this
    function uses one HTTP request for the whole selection.
    """

    iso3_codes = [wdi_client.normalize_iso3(country) for country in countries]
    if not iso3_codes:
        return {}
    if years <= 0:
        raise ValueError("years must be a positive integer")

    rows = _fetch_population_rows(iso3_codes, years=years, timeout=timeout)
    grouped: dict[str, list[dict[str, Any]]] = {iso3: [] for iso3 in iso3_codes}
    for row in rows:
        iso3 = wdi_client.row_country_iso3(row)
        if iso3 in grouped:
            grouped[iso3].append(row)

    results: dict[str, dict[str, Any]] = {}
    for iso3 in iso3_codes:
        population = _select_recent_population(grouped[iso3], years=years)
        if not population:
            continue
        results[iso3] = {
            "country": iso3,
            "source": "World Bank World Development Indicators",
            "indicator": POPULATION_INDICATOR_ID,
            "indicator_name": "Population, total",
            "unit": "persons",
            "years": population,
        }
    return results


def get_gdp_data(
    country: str,
    *,
    years: int = 10,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    """Return recent WDI GDP data for an ISO 3166 alpha-3 country code.

    GDP values are returned in current US dollars using World Development
    Indicators indicator NY.GDP.MKTP.CD, GDP (current US$).
    """

    iso3 = wdi_client.normalize_iso3(country)
    if years <= 0:
        raise ValueError("years must be a positive integer")

    rows = _fetch_gdp_rows([iso3], years=years, timeout=timeout)
    gdp = _select_recent_gdp(rows, years=years)
    if not gdp:
        raise GdpDataError(f"No GDP data returned for {iso3}")

    return {
        "country": iso3,
        "source": "World Bank World Development Indicators",
        "indicator": GDP_INDICATOR_ID,
        "indicator_name": "GDP (current US$)",
        "unit": "current US$",
        "years": gdp,
    }


def get_gdp_data_many(
    countries: list[str],
    *,
    years: int = 10,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
) -> dict[str, dict[str, Any]]:
    """Return recent WDI GDP data for multiple ISO3 country codes."""

    iso3_codes = [wdi_client.normalize_iso3(country) for country in countries]
    if not iso3_codes:
        return {}
    if years <= 0:
        raise ValueError("years must be a positive integer")

    rows = _fetch_gdp_rows(iso3_codes, years=years, timeout=timeout)
    grouped: dict[str, list[dict[str, Any]]] = {iso3: [] for iso3 in iso3_codes}
    for row in rows:
        iso3 = wdi_client.row_country_iso3(row)
        if iso3 in grouped:
            grouped[iso3].append(row)

    results: dict[str, dict[str, Any]] = {}
    for iso3 in iso3_codes:
        gdp = _select_recent_gdp(grouped[iso3], years=years)
        if not gdp:
            continue
        results[iso3] = {
            "country": iso3,
            "source": "World Bank World Development Indicators",
            "indicator": GDP_INDICATOR_ID,
            "indicator_name": "GDP (current US$)",
            "unit": "current US$",
            "years": gdp,
        }
    return results


def get_gdp_per_capita_data(
    country: str,
    *,
    years: int = 10,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    """Return recent WDI GDP per capita data for an ISO 3166 alpha-3 country.

    GDP per capita values are returned in current US dollars using World
    Development Indicators indicator NY.GDP.PCAP.CD, GDP per capita
    (current US$).
    """

    iso3 = wdi_client.normalize_iso3(country)
    if years <= 0:
        raise ValueError("years must be a positive integer")

    rows = _fetch_gdp_per_capita_rows([iso3], years=years, timeout=timeout)
    gdp_per_capita = _select_recent_gdp_per_capita(rows, years=years)
    if not gdp_per_capita:
        raise GdpPerCapitaDataError(f"No GDP per capita data returned for {iso3}")

    return {
        "country": iso3,
        "source": "World Bank World Development Indicators",
        "indicator": GDP_PER_CAPITA_INDICATOR_ID,
        "indicator_name": "GDP per capita (current US$)",
        "unit": "current US$",
        "years": gdp_per_capita,
    }


def get_gdp_per_capita_data_many(
    countries: list[str],
    *,
    years: int = 10,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
) -> dict[str, dict[str, Any]]:
    """Return recent WDI GDP per capita data for multiple ISO3 country codes."""

    iso3_codes = [wdi_client.normalize_iso3(country) for country in countries]
    if not iso3_codes:
        return {}
    if years <= 0:
        raise ValueError("years must be a positive integer")

    rows = _fetch_gdp_per_capita_rows(iso3_codes, years=years, timeout=timeout)
    grouped: dict[str, list[dict[str, Any]]] = {iso3: [] for iso3 in iso3_codes}
    for row in rows:
        iso3 = wdi_client.row_country_iso3(row)
        if iso3 in grouped:
            grouped[iso3].append(row)

    results: dict[str, dict[str, Any]] = {}
    for iso3 in iso3_codes:
        gdp_per_capita = _select_recent_gdp_per_capita(grouped[iso3], years=years)
        if not gdp_per_capita:
            continue
        results[iso3] = {
            "country": iso3,
            "source": "World Bank World Development Indicators",
            "indicator": GDP_PER_CAPITA_INDICATOR_ID,
            "indicator_name": "GDP per capita (current US$)",
            "unit": "current US$",
            "years": gdp_per_capita,
        }
    return results


def _fetch_population_rows(
    iso3_codes: list[str],
    *,
    years: int,
    timeout: int,
) -> list[dict[str, Any]]:
    return wdi_client.fetch_indicator_rows(
        iso3_codes,
        indicator=POPULATION_INDICATOR_ID,
        years=years,
        timeout=timeout,
    )


def _fetch_gdp_rows(
    iso3_codes: list[str],
    *,
    years: int,
    timeout: int,
) -> list[dict[str, Any]]:
    return wdi_client.fetch_indicator_rows(
        iso3_codes,
        indicator=GDP_INDICATOR_ID,
        years=years,
        timeout=timeout,
    )


def _fetch_gdp_per_capita_rows(
    iso3_codes: list[str],
    *,
    years: int,
    timeout: int,
) -> list[dict[str, Any]]:
    return wdi_client.fetch_indicator_rows(
        iso3_codes,
        indicator=GDP_PER_CAPITA_INDICATOR_ID,
        years=years,
        timeout=timeout,
    )


def _select_recent_population(
    rows: list[dict[str, Any]],
    *,
    years: int,
) -> list[dict[str, int]]:
    values = wdi_client.select_recent_indicator_values(
        rows,
        years=years,
        value_key="population",
    )
    return [
        {"year": int(row["year"]), "population": round(row["population"])}
        for row in values
    ]


def _select_recent_gdp(
    rows: list[dict[str, Any]],
    *,
    years: int,
) -> list[dict[str, int | float]]:
    return wdi_client.select_recent_indicator_values(
        rows,
        years=years,
        value_key="gdp",
    )


def _select_recent_gdp_per_capita(
    rows: list[dict[str, Any]],
    *,
    years: int,
) -> list[dict[str, int | float]]:
    return wdi_client.select_recent_indicator_values(
        rows,
        years=years,
        value_key="gdp_per_capita",
    )
