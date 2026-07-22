from __future__ import annotations

import argparse
import json
import sys

from wdi_experiments import indicators

get_population_data = indicators.get_population_data
get_population_data_many = indicators.get_population_data_many
get_gdp_data = indicators.get_gdp_data
get_gdp_data_many = indicators.get_gdp_data_many
get_gdp_per_capita_data = indicators.get_gdp_per_capita_data
get_gdp_per_capita_data_many = indicators.get_gdp_per_capita_data_many
PopulationDataError = indicators.PopulationDataError
GdpDataError = indicators.GdpDataError
GdpPerCapitaDataError = indicators.GdpPerCapitaDataError


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Fetch recent WDI data for an ISO 3166 alpha-3 country."
    )
    parser.add_argument(
        "indicator",
        type=str.lower,
        choices=["population", "gdp", "gdp-per-capita"],
        help="WDI indicator to fetch.",
    )
    parser.add_argument("country", help="ISO 3166 alpha-3 country code, e.g. JPN")
    parser.add_argument(
        "--years",
        type=int,
        default=10,
        help="Number of recent years to return. Defaults to 10.",
    )
    args = parser.parse_args(argv)

    try:
        if args.indicator == "gdp":
            result = indicators.get_gdp_data(args.country, years=args.years)
        elif args.indicator == "gdp-per-capita":
            result = indicators.get_gdp_per_capita_data(
                args.country, years=args.years
            )
        else:
            result = indicators.get_population_data(args.country, years=args.years)
    except (
        PopulationDataError,
        GdpDataError,
        GdpPerCapitaDataError,
        ValueError,
    ) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
