from __future__ import annotations

import csv
import importlib
import json
import sys
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import altair as alt
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

wdi = importlib.import_module("wdi_experiments.main")
wdi_indicators = importlib.import_module("wdi_experiments.indicators")
wdi_client = importlib.import_module("wdi_experiments.wdi_client")


ONE_MONTH_SECONDS = 30 * 24 * 60 * 60
WDI_TIMEOUT_SECONDS = wdi_client.DEFAULT_TIMEOUT_SECONDS
DISK_CACHE_PATH = ROOT / ".cache" / "streamlit-wdi" / "data.json"

COUNTRY_REGION_CODES_PATH = ROOT / "apps" / "streamlit" / "wdi_country_region_code.csv"


def load_countries(path: Path = COUNTRY_REGION_CODES_PATH) -> dict[str, str]:
    with path.open(encoding="utf-8-sig", newline="") as country_file:
        rows = list(csv.DictReader(country_file))

    countries: dict[str, str] = {}
    for row in rows:
        code = row.get("country_region_code", "").strip().upper()
        label = row.get("short_name_wdi", "").strip()
        if not code or not label:
            continue

        countries[label] = code

    return countries


COUNTRIES = load_countries()


@dataclass(frozen=True)
class IndicatorOption:
    label: str
    indicator_id: str
    value_key: str
    fetch_many: Callable[..., dict[str, dict[str, Any]]]
    error_type: type[Exception]


@dataclass(frozen=True)
class ChartResult:
    data: pd.DataFrame
    errors: list[str]
    indicator_name: str
    indicator_id: str
    unit: str


@dataclass(frozen=True)
class CachedBatch:
    results: dict[str, dict[str, Any]]
    cached_iso3_codes: set[str]


INDICATORS = {
    "Population": IndicatorOption(
        label="Population",
        indicator_id=wdi_indicators.POPULATION_INDICATOR_ID,
        value_key="population",
        fetch_many=wdi.get_population_data_many,
        error_type=wdi.PopulationDataError,
    ),
    "GDP": IndicatorOption(
        label="GDP",
        indicator_id=wdi_indicators.GDP_INDICATOR_ID,
        value_key="gdp",
        fetch_many=wdi.get_gdp_data_many,
        error_type=wdi.GdpDataError,
    ),
    "GDP per capita": IndicatorOption(
        label="GDP per capita",
        indicator_id=wdi_indicators.GDP_PER_CAPITA_INDICATOR_ID,
        value_key="gdp_per_capita",
        fetch_many=wdi.get_gdp_per_capita_data_many,
        error_type=wdi.GdpPerCapitaDataError,
    ),
}


st.set_page_config(page_title="WDI Explorer", page_icon="chart", layout="wide")


@st.cache_data(ttl=ONE_MONTH_SECONDS)
def load_indicator_batch(
    indicator_label: str,
    country_iso3_codes: tuple[str, ...],
    years: int,
) -> dict[str, dict[str, Any]]:
    cached_batch = read_cached_batch(
        indicator_label,
        country_iso3_codes,
        years,
    )
    missing_iso3_codes = [
        iso3
        for iso3 in country_iso3_codes
        if iso3 not in cached_batch.cached_iso3_codes
    ]
    if not missing_iso3_codes:
        return cached_batch.results

    indicator = INDICATORS[indicator_label]
    fetched_results = fetch_indicator_with_retry(
        indicator,
        missing_iso3_codes,
        years=years,
    )
    write_cached_results(
        indicator_label,
        years,
        tuple(missing_iso3_codes),
        fetched_results,
    )
    return cached_batch.results | fetched_results


def fetch_indicator_with_retry(
    indicator: IndicatorOption,
    iso3_codes: list[str],
    *,
    years: int,
) -> dict[str, dict[str, Any]]:
    try:
        return indicator.fetch_many(
            iso3_codes,
            years=years,
            timeout=WDI_TIMEOUT_SECONDS,
        )
    except indicator.error_type as exc:
        if "timed out" not in str(exc).lower():
            raise
        return indicator.fetch_many(
            iso3_codes,
            years=years,
            timeout=WDI_TIMEOUT_SECONDS,
        )


def read_disk_cache() -> dict[str, Any]:
    if not DISK_CACHE_PATH.exists():
        return {}

    try:
        with DISK_CACHE_PATH.open(encoding="utf-8") as cache_file:
            cache = json.load(cache_file)
    except (OSError, json.JSONDecodeError):
        return {}

    if not isinstance(cache, dict):
        return {}
    return cache


def write_disk_cache(cache: dict[str, Any]) -> None:
    DISK_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    temp_path = DISK_CACHE_PATH.with_suffix(".tmp")
    with temp_path.open("w", encoding="utf-8") as cache_file:
        json.dump(cache, cache_file, indent=2, sort_keys=True)
    temp_path.replace(DISK_CACHE_PATH)


def cache_key(indicator_label: str, years: int, country_iso3: str) -> str:
    return f"{indicator_label}|{years}|{country_iso3}"


def read_cached_batch(
    indicator_label: str,
    country_iso3_codes: tuple[str, ...],
    years: int,
) -> CachedBatch:
    cache = read_disk_cache()
    now = time.time()
    results: dict[str, dict[str, Any]] = {}
    cached_iso3_codes: set[str] = set()

    for country_iso3 in country_iso3_codes:
        entry = cache.get(cache_key(indicator_label, years, country_iso3))
        if not isinstance(entry, dict):
            continue

        fetched_at = entry.get("fetched_at")
        data = entry.get("data")
        if not isinstance(fetched_at, int | float):
            continue
        if now - fetched_at > ONE_MONTH_SECONDS:
            continue
        if not isinstance(data, dict):
            continue

        cached_iso3_codes.add(country_iso3)
        results[country_iso3] = data

    return CachedBatch(results=results, cached_iso3_codes=cached_iso3_codes)


def write_cached_results(
    indicator_label: str,
    years: int,
    country_iso3_codes: tuple[str, ...],
    results: dict[str, dict[str, Any]],
) -> None:
    if not country_iso3_codes:
        return

    cache = read_disk_cache()
    fetched_at = time.time()
    for country_iso3 in country_iso3_codes:
        if country_iso3 not in results:
            continue
        cache[cache_key(indicator_label, years, country_iso3)] = {
            "fetched_at": fetched_at,
            "data": results[country_iso3],
        }
    write_disk_cache(cache)


def build_chart_data(
    selected_countries: list[str],
    country_options: dict[str, str],
    indicator_label: str,
    years: int,
) -> ChartResult:
    indicator = INDICATORS[indicator_label]
    iso3_by_name = {
        country_name: country_options[country_name]
        for country_name in selected_countries
    }
    empty_data = pd.DataFrame(
        columns=["year", "country", "indicator_id", "indicator_name", "value"]
    )

    try:
        results = load_indicator_batch(
            indicator.label,
            tuple(iso3_by_name.values()),
            years,
        )
    except (indicator.error_type, ValueError) as exc:
        return ChartResult(
            data=empty_data,
            errors=[str(exc)],
            indicator_name=indicator.label,
            indicator_id=indicator.indicator_id,
            unit="",
        )

    frames: list[pd.DataFrame] = []
    errors: list[str] = []
    indicator_name = indicator.label
    indicator_id = indicator.indicator_id
    unit = ""

    for country_name, country_iso3 in iso3_by_name.items():
        result = results.get(country_iso3)
        if result is None:
            errors.append(f"{country_name}: no {indicator.label.lower()} data returned")
            continue

        frame = pd.DataFrame(result["years"])
        if indicator.value_key not in frame:
            errors.append(
                f"{country_name}: unexpected {indicator.label.lower()} data shape"
            )
            continue

        frame = frame.rename(columns={indicator.value_key: "value"})
        frame["country"] = country_name
        indicator_name = str(result.get("indicator_name") or indicator.label)
        indicator_id = str(result.get("indicator") or indicator.indicator_id)
        frame["indicator_id"] = indicator_id
        frame["indicator_name"] = indicator_name
        frames.append(
            frame[["year", "country", "indicator_id", "indicator_name", "value"]]
        )
        unit = str(result.get("unit") or unit)

    if not frames:
        return ChartResult(
            data=empty_data,
            errors=errors,
            indicator_name=indicator_name,
            indicator_id=indicator_id,
            unit=unit,
        )

    return ChartResult(
        data=pd.concat(frames, ignore_index=True),
        errors=errors,
        indicator_name=indicator_name,
        indicator_id=indicator_id,
        unit=unit,
    )


def value_axis_title(chart_result: ChartResult) -> str:
    if not chart_result.unit:
        return chart_result.indicator_name
    return f"{chart_result.indicator_name} ({chart_result.unit})"


header = st.columns([1, 0.25])
with header[0]:
    st.title("WDI Explorer")
with header[1]:
    st.link_button("Back to yeiichi.com", "https://yeiichi.com")

st.warning(
    "This app is for experimental purposes. For serious research, citation, "
    "please use the official World Development Indicators DataBank."
)

with st.expander("References", expanded=False):
    st.markdown(
        """
        - [World Development Indicators DataBank](https://databank.worldbank.org/source/world-development-indicators)
        - [World Bank API developer information](https://datahelpdesk.worldbank.org/knowledgebase/topics/125589-developer-information)

        [![GitHub repository](https://img.shields.io/badge/GitHub-yeiichi%2Fwdi--experiments-24292f?logo=github&logoColor=white)](https://github.com/yeiichi/wdi-experiments)
        """
    )

country_options = dict(sorted(COUNTRIES.items()))
default_countries = [
    country
    for country in ("Japan", "United States", "India")
    if country in country_options
]

with st.form("wdi-query"):
    controls = st.columns([2, 3, 1])
    with controls[0]:
        indicator_label = st.selectbox(
            "Indicator",
            options=list(INDICATORS),
            index=0,
            format_func=lambda label: (
                f"{INDICATORS[label].label} ({INDICATORS[label].indicator_id})"
            ),
        )
    with controls[1]:
        selected_countries = st.multiselect(
            "Countries/Regions",
            options=list(country_options),
            default=default_countries[:2],
        )
    with controls[2]:
        years = st.number_input(
            "Years",
            min_value=1,
            max_value=60,
            value=10,
            step=1,
        )

    fetch = st.form_submit_button(
        "Fetch",
        type="primary",
        disabled=not selected_countries,
    )

if not selected_countries:
    st.info("Choose at least one country.")
    st.stop()

if not fetch:
    st.info("Press Fetch to request WDI data.")
    st.stop()

with st.spinner("Fetching cached WDI data..."):
    chart_result = build_chart_data(
        selected_countries,
        country_options,
        indicator_label,
        int(years),
    )
    chart_data = chart_result.data

for error in chart_result.errors:
    st.warning(error)

if chart_data.empty:
    st.warning("No WDI data found for the selected countries.")
    st.stop()

chart = (
    alt.Chart(chart_data)
    .mark_line(point=True)
    .encode(
        x=alt.X(
            "year:Q",
            axis=alt.Axis(format="d", title="Year"),
            scale=alt.Scale(zero=False),
        ),
        y=alt.Y("value:Q", axis=alt.Axis(title=value_axis_title(chart_result))),
        color=alt.Color("country:N", title="Country"),
        tooltip=[
            alt.Tooltip("country:N", title="Country"),
            alt.Tooltip("year:Q", title="Year", format="d"),
            alt.Tooltip("value:Q", title=chart_result.indicator_name, format=",.2f"),
        ],
    )
)

st.altair_chart(chart, width="stretch")

st.caption(f"Indicator ID: `{chart_result.indicator_id}`")

with st.expander("Data", expanded=False):
    display_data = chart_data.rename(
        columns={"value": chart_result.indicator_name}
    ).sort_values(["country", "year"])
    st.dataframe(display_data.reset_index(drop=True), width="stretch", hide_index=True)
    st.download_button(
        "Download CSV",
        data=display_data.to_csv(index=False).encode("utf-8"),
        file_name=f"wdi-{chart_result.indicator_id.lower()}-{int(years)}y.csv",
        mime="text/csv",
    )
