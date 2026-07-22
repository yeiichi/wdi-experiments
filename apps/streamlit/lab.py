from __future__ import annotations

import importlib
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import altair as alt
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) in sys.path:
    sys.path.remove(str(SRC))
sys.path.insert(0, str(SRC))

importlib.invalidate_caches()
sys.modules.pop("wdi_experiments.cli", None)
sys.modules.pop("wdi_experiments.main", None)
sys.modules.pop("wdi_experiments", None)
project_cli = importlib.import_module("wdi_experiments.cli")
PopulationDataError = project_cli.PopulationDataError
get_population_data_many = project_cli.get_population_data_many


ONE_MONTH_SECONDS = 30 * 24 * 60 * 60
POPULATION_TIMEOUT_SECONDS = 12
COUNTRIES = {
    "Argentina": "ARG",
    "Australia": "AUS",
    "Austria": "AUT",
    "Bangladesh": "BGD",
    "Belgium": "BEL",
    "Brazil": "BRA",
    "Canada": "CAN",
    "Chile": "CHL",
    "China": "CHN",
    "Colombia": "COL",
    "Denmark": "DNK",
    "Egypt, Arab Rep.": "EGY",
    "Finland": "FIN",
    "France": "FRA",
    "Germany": "DEU",
    "Greece": "GRC",
    "India": "IND",
    "Indonesia": "IDN",
    "Italy": "ITA",
    "Japan": "JPN",
    "Kenya": "KEN",
    "Korea, Rep.": "KOR",
    "Mexico": "MEX",
    "Netherlands": "NLD",
    "Nigeria": "NGA",
    "Norway": "NOR",
    "Pakistan": "PAK",
    "Philippines": "PHL",
    "Poland": "POL",
    "Russian Federation": "RUS",
    "Saudi Arabia": "SAU",
    "South Africa": "ZAF",
    "Spain": "ESP",
    "Sweden": "SWE",
    "Switzerland": "CHE",
    "Thailand": "THA",
    "Turkiye": "TUR",
    "United Kingdom": "GBR",
    "United States": "USA",
    "Vietnam": "VNM",
}


@dataclass(frozen=True)
class ChartResult:
    data: pd.DataFrame
    errors: list[str]


st.set_page_config(page_title="WDI Population", page_icon="chart", layout="wide")


@st.cache_data(ttl=ONE_MONTH_SECONDS)
def load_population_batch(
    country_iso3_codes: tuple[str, ...], years: int
) -> dict[str, Any]:
    return get_population_data_many(
        list(country_iso3_codes), years=years, timeout=POPULATION_TIMEOUT_SECONDS
    )


def build_chart_data(
    selected_countries: list[str], country_options: dict[str, str], years: int
) -> ChartResult:
    frames: list[pd.DataFrame] = []
    errors: list[str] = []
    iso3_by_name = {
        country_name: country_options[country_name]
        for country_name in selected_countries
    }

    try:
        results = load_population_batch(tuple(iso3_by_name.values()), years)
    except PopulationDataError as exc:
        return ChartResult(
            data=pd.DataFrame(columns=["year", "country", "population"]),
            errors=[str(exc)],
        )

    for country_name, country_iso3 in iso3_by_name.items():
        result = results.get(country_iso3)
        if result is None:
            errors.append(f"{country_name}: no population data returned")
            continue
        frame = pd.DataFrame(result["years"])
        frame["country"] = country_name
        frames.append(frame)

    if not frames:
        data = pd.DataFrame(columns=["year", "country", "population"])
        return ChartResult(data=data, errors=errors)

    return ChartResult(data=pd.concat(frames, ignore_index=True), errors=errors)


st.title("WDI Population")

country_options = dict(sorted(COUNTRIES.items()))
default_countries = [
    country
    for country in ("Japan", "United States", "India")
    if country in country_options
]

controls = st.columns([3, 1])
with controls[0]:
    selected_countries = st.multiselect(
        "Country",
        options=list(country_options),
        default=default_countries[:2],
        help="English country names mapped locally to ISO 3166 alpha-3 codes.",
    )
with controls[1]:
    years = st.number_input(
        "Period (years)",
        min_value=1,
        max_value=60,
        value=10,
        step=1,
    )

fetch = st.button("Fetch", type="primary", disabled=not selected_countries)

if not selected_countries:
    st.info("Choose at least one country.")
    st.stop()

if not fetch:
    st.info("Press Fetch to request population data.")
    st.stop()

with st.spinner("Fetching cached WDI population data..."):
    chart_result = build_chart_data(selected_countries, country_options, int(years))
    chart_data = chart_result.data

for error in chart_result.errors:
    st.warning(error)

if chart_data.empty:
    st.warning("No population data found for the selected countries.")
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
        y=alt.Y("population:Q", axis=alt.Axis(title="Population")),
        color=alt.Color("country:N", title="Country"),
        tooltip=[
            alt.Tooltip("country:N", title="Country"),
            alt.Tooltip("year:Q", title="Year", format="d"),
            alt.Tooltip("population:Q", title="Population", format=","),
        ],
    )
)

st.altair_chart(chart, width="stretch")

with st.expander("Data", expanded=False):
    display_data = chart_data.sort_values(["country", "year"]).reset_index(drop=True)
    st.dataframe(display_data, width="stretch", hide_index=True)
