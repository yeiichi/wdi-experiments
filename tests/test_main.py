import json
from urllib.error import HTTPError, URLError

import pytest

from wdi_experiments import indicators
from wdi_experiments import cli as app
from wdi_experiments import wdi_client


def test_get_population_data_returns_recent_sorted_values(monkeypatch) -> None:
    rows = [
        {"date": "2025", "value": 123366734},
        {"date": "2024", "value": 123975371.4},
        {"date": "2023", "value": None},
        {"date": "not-a-year", "value": 1},
        {"date": "2022", "value": "125124989"},
    ]

    def fake_fetch_population_rows(
        iso3_codes: list[str], *, years: int, timeout: int
    ) -> list[dict[str, object]]:
        assert iso3_codes == ["JPN"]
        assert years == 3
        assert timeout == indicators.DEFAULT_TIMEOUT_SECONDS
        return rows

    monkeypatch.setattr(
        indicators, "_fetch_population_rows", fake_fetch_population_rows
    )

    result = indicators.get_population_data(" jpn ", years=3)

    assert result == {
        "country": "JPN",
        "source": "World Bank World Development Indicators",
        "indicator": "SP.POP.TOTL",
        "indicator_name": "Population, total",
        "unit": "persons",
        "years": [
            {"year": 2022, "population": 125124989},
            {"year": 2024, "population": 123975371},
            {"year": 2025, "population": 123366734},
        ],
    }


@pytest.mark.parametrize("country", ["JP", "JPN1", "", "12A"])
def test_get_population_data_rejects_invalid_iso3(country: str) -> None:
    with pytest.raises(ValueError, match="ISO 3166 alpha-3"):
        indicators.get_population_data(country)


def test_get_population_data_rejects_non_positive_years() -> None:
    with pytest.raises(ValueError, match="positive integer"):
        indicators.get_population_data("JPN", years=0)


def test_get_population_data_raises_when_no_values(monkeypatch) -> None:
    monkeypatch.setattr(
        indicators,
        "_fetch_population_rows",
        lambda iso3_codes, *, years, timeout: [{"date": "2025", "value": None}],
    )

    with pytest.raises(indicators.PopulationDataError, match="No population data"):
        indicators.get_population_data("JPN")


def test_get_population_data_many_groups_rows_by_country(monkeypatch) -> None:
    rows = [
        {"countryiso3code": "JPN", "date": "2025", "value": 123366734},
        {"countryiso3code": "USA", "date": "2025", "value": 340110988},
        {"countryiso3code": "USA", "date": "2024", "value": 337000000},
    ]

    def fake_fetch_population_rows(
        iso3_codes: list[str], *, years: int, timeout: int
    ) -> list[dict[str, object]]:
        assert iso3_codes == ["JPN", "USA"]
        assert years == 2
        assert timeout == indicators.DEFAULT_TIMEOUT_SECONDS
        return rows

    monkeypatch.setattr(
        indicators, "_fetch_population_rows", fake_fetch_population_rows
    )

    result = indicators.get_population_data_many(["jpn", "usa"], years=2)

    assert result["JPN"]["years"] == [{"year": 2025, "population": 123366734}]
    assert result["USA"]["years"] == [
        {"year": 2024, "population": 337000000},
        {"year": 2025, "population": 340110988},
    ]


def test_get_gdp_data_returns_recent_sorted_values(monkeypatch) -> None:
    rows = [
        {"date": "2025", "value": 4_200_000_000_000.5},
        {"date": "2024", "value": "4100000000000"},
        {"date": "2023", "value": None},
        {"date": "not-a-year", "value": 1},
    ]

    def fake_fetch_gdp_rows(
        iso3_codes: list[str], *, years: int, timeout: int
    ) -> list[dict[str, object]]:
        assert iso3_codes == ["JPN"]
        assert years == 2
        assert timeout == indicators.DEFAULT_TIMEOUT_SECONDS
        return rows

    monkeypatch.setattr(indicators, "_fetch_gdp_rows", fake_fetch_gdp_rows)

    result = indicators.get_gdp_data(" jpn ", years=2)

    assert result == {
        "country": "JPN",
        "source": "World Bank World Development Indicators",
        "indicator": "NY.GDP.MKTP.CD",
        "indicator_name": "GDP (current US$)",
        "unit": "current US$",
        "years": [
            {"year": 2024, "gdp": 4100000000000.0},
            {"year": 2025, "gdp": 4200000000000.5},
        ],
    }


def test_get_gdp_data_raises_when_no_values(monkeypatch) -> None:
    monkeypatch.setattr(
        indicators,
        "_fetch_gdp_rows",
        lambda iso3_codes, *, years, timeout: [{"date": "2025", "value": None}],
    )

    with pytest.raises(indicators.GdpDataError, match="No GDP data"):
        indicators.get_gdp_data("JPN")


def test_get_gdp_data_many_groups_rows_by_country(monkeypatch) -> None:
    rows = [
        {"countryiso3code": "JPN", "date": "2025", "value": 4_200_000_000_000},
        {"countryiso3code": "USA", "date": "2025", "value": 29_000_000_000_000},
        {"countryiso3code": "USA", "date": "2024", "value": 28_000_000_000_000},
    ]

    def fake_fetch_gdp_rows(
        iso3_codes: list[str], *, years: int, timeout: int
    ) -> list[dict[str, object]]:
        assert iso3_codes == ["JPN", "USA"]
        assert years == 2
        assert timeout == indicators.DEFAULT_TIMEOUT_SECONDS
        return rows

    monkeypatch.setattr(indicators, "_fetch_gdp_rows", fake_fetch_gdp_rows)

    result = indicators.get_gdp_data_many(["jpn", "usa"], years=2)

    assert result["JPN"]["years"] == [{"year": 2025, "gdp": 4200000000000.0}]
    assert result["USA"]["years"] == [
        {"year": 2024, "gdp": 28000000000000.0},
        {"year": 2025, "gdp": 29000000000000.0},
    ]


def test_fetch_gdp_rows_uses_gdp_indicator(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def fake_fetch_indicator_rows(
        iso3_codes: list[str], *, indicator: str, years: int, timeout: int
    ) -> list[dict[str, object]]:
        captured["iso3_codes"] = iso3_codes
        captured["indicator"] = indicator
        captured["years"] = years
        captured["timeout"] = timeout
        return [{"date": "2025", "value": 123}]

    monkeypatch.setattr(wdi_client, "fetch_indicator_rows", fake_fetch_indicator_rows)

    rows = indicators._fetch_gdp_rows(["JPN"], years=10, timeout=7)

    assert rows == [{"date": "2025", "value": 123}]
    assert captured == {
        "iso3_codes": ["JPN"],
        "indicator": "NY.GDP.MKTP.CD",
        "years": 10,
        "timeout": 7,
    }


def test_get_gdp_per_capita_data_returns_recent_sorted_values(monkeypatch) -> None:
    rows = [
        {"date": "2025", "value": 33834.392},
        {"date": "2024", "value": "33000.5"},
        {"date": "2023", "value": None},
        {"date": "not-a-year", "value": 1},
    ]

    def fake_fetch_gdp_per_capita_rows(
        iso3_codes: list[str], *, years: int, timeout: int
    ) -> list[dict[str, object]]:
        assert iso3_codes == ["JPN"]
        assert years == 2
        assert timeout == indicators.DEFAULT_TIMEOUT_SECONDS
        return rows

    monkeypatch.setattr(
        indicators,
        "_fetch_gdp_per_capita_rows",
        fake_fetch_gdp_per_capita_rows,
    )

    result = indicators.get_gdp_per_capita_data(" jpn ", years=2)

    assert result == {
        "country": "JPN",
        "source": "World Bank World Development Indicators",
        "indicator": "NY.GDP.PCAP.CD",
        "indicator_name": "GDP per capita (current US$)",
        "unit": "current US$",
        "years": [
            {"year": 2024, "gdp_per_capita": 33000.5},
            {"year": 2025, "gdp_per_capita": 33834.392},
        ],
    }


def test_get_gdp_per_capita_data_raises_when_no_values(monkeypatch) -> None:
    monkeypatch.setattr(
        indicators,
        "_fetch_gdp_per_capita_rows",
        lambda iso3_codes, *, years, timeout: [{"date": "2025", "value": None}],
    )

    with pytest.raises(
        indicators.GdpPerCapitaDataError, match="No GDP per capita data"
    ):
        indicators.get_gdp_per_capita_data("JPN")


def test_get_gdp_per_capita_data_many_groups_rows_by_country(monkeypatch) -> None:
    rows = [
        {"countryiso3code": "JPN", "date": "2025", "value": 33834.392},
        {"countryiso3code": "USA", "date": "2025", "value": 82769.412},
        {"countryiso3code": "USA", "date": "2024", "value": 81695.187},
    ]

    def fake_fetch_gdp_per_capita_rows(
        iso3_codes: list[str], *, years: int, timeout: int
    ) -> list[dict[str, object]]:
        assert iso3_codes == ["JPN", "USA"]
        assert years == 2
        assert timeout == indicators.DEFAULT_TIMEOUT_SECONDS
        return rows

    monkeypatch.setattr(
        indicators,
        "_fetch_gdp_per_capita_rows",
        fake_fetch_gdp_per_capita_rows,
    )

    result = indicators.get_gdp_per_capita_data_many(["jpn", "usa"], years=2)

    assert result["JPN"]["years"] == [
        {"year": 2025, "gdp_per_capita": 33834.392}
    ]
    assert result["USA"]["years"] == [
        {"year": 2024, "gdp_per_capita": 81695.187},
        {"year": 2025, "gdp_per_capita": 82769.412},
    ]


def test_fetch_gdp_per_capita_rows_uses_gdp_per_capita_indicator(
    monkeypatch,
) -> None:
    captured: dict[str, object] = {}

    def fake_fetch_indicator_rows(
        iso3_codes: list[str], *, indicator: str, years: int, timeout: int
    ) -> list[dict[str, object]]:
        captured["iso3_codes"] = iso3_codes
        captured["indicator"] = indicator
        captured["years"] = years
        captured["timeout"] = timeout
        return [{"date": "2025", "value": 123}]

    monkeypatch.setattr(wdi_client, "fetch_indicator_rows", fake_fetch_indicator_rows)

    rows = indicators._fetch_gdp_per_capita_rows(["JPN"], years=10, timeout=7)

    assert rows == [{"date": "2025", "value": 123}]
    assert captured == {
        "iso3_codes": ["JPN"],
        "indicator": "NY.GDP.PCAP.CD",
        "years": 10,
        "timeout": 7,
    }


def test_fetch_population_rows_builds_world_bank_request(monkeypatch) -> None:
    captured: dict[str, object] = {}

    monkeypatch.setattr(
        wdi_client, "year_range_for_recent_values", lambda years: (2015, 2025)
    )

    def fake_fetch_json(url: str, *, timeout: int) -> list[object]:
        captured["url"] = url
        captured["timeout"] = timeout
        return [{}, [{"date": "2025", "value": 123}]]

    monkeypatch.setattr(wdi_client, "fetch_json", fake_fetch_json)

    rows = wdi_client.fetch_indicator_rows(
        ["JPN", "USA"], indicator="SP.POP.TOTL", years=10, timeout=7
    )

    assert rows == [{"date": "2025", "value": 123}]
    assert captured["timeout"] == 7
    assert captured["url"] == (
        "https://api.worldbank.org/v2/country/JPN;USA/indicator/SP.POP.TOTL"
        "?format=json&date=2015%3A2025&per_page=22"
    )


def test_year_range_for_recent_values_includes_current_year(monkeypatch) -> None:
    class FakeDateTime:
        @classmethod
        def now(cls, timezone: object) -> object:
            class FakeNow:
                year = 2026

            return FakeNow()

    monkeypatch.setattr(wdi_client, "datetime", FakeDateTime)

    assert wdi_client.year_range_for_recent_values(60) == (1966, 2026)


def test_payload_rows_raises_world_bank_message() -> None:
    payload = [
        {"message": [{"key": "Invalid value", "value": "Country code is invalid"}]},
        None,
    ]

    with pytest.raises(
        wdi_client.WorldBankDataError, match="Invalid value: Country code is invalid"
    ):
        wdi_client.payload_rows(payload)


@pytest.mark.parametrize("payload", [{}, [], [{}, {}]])
def test_payload_rows_rejects_unexpected_shapes(payload: object) -> None:
    with pytest.raises(wdi_client.WorldBankDataError, match="unexpected"):
        wdi_client.payload_rows(payload)


def test_fetch_json_decodes_success(monkeypatch) -> None:
    class FakeResponse:
        def __enter__(self) -> "FakeResponse":
            return self

        def __exit__(self, *args: object) -> None:
            return None

        def read(self) -> bytes:
            return b'[{"page": 1}, []]'

    def fake_urlopen(request: object, timeout: int) -> FakeResponse:
        captured["headers"] = request.header_items()
        captured["timeout"] = timeout
        return FakeResponse()

    captured: dict[str, object] = {}
    monkeypatch.setattr(wdi_client, "urlopen", fake_urlopen)

    assert wdi_client.fetch_json("https://example.test", timeout=5) == [
        {"page": 1},
        [],
    ]
    assert captured["timeout"] == 5
    assert ("Accept", "application/json") in captured["headers"]


def test_fetch_json_wraps_http_error(monkeypatch) -> None:
    class FakeHTTPError(HTTPError):
        def read(self) -> bytes:
            return b"bad request"

    def fake_urlopen(request: object, timeout: int) -> object:
        raise FakeHTTPError("https://example.test", 400, "Bad Request", {}, None)

    monkeypatch.setattr(wdi_client, "urlopen", fake_urlopen)

    with pytest.raises(wdi_client.WorldBankDataError, match="HTTP 400: bad request"):
        wdi_client.fetch_json("https://example.test", timeout=5)


def test_fetch_json_wraps_url_error(monkeypatch) -> None:
    def fake_urlopen(request: object, timeout: int) -> object:
        raise URLError("network down")

    monkeypatch.setattr(wdi_client, "urlopen", fake_urlopen)

    with pytest.raises(wdi_client.WorldBankDataError, match="network down"):
        wdi_client.fetch_json("https://example.test", timeout=5)


def test_fetch_json_wraps_timeout_error(monkeypatch) -> None:
    def fake_urlopen(request: object, timeout: int) -> object:
        raise TimeoutError

    monkeypatch.setattr(wdi_client, "urlopen", fake_urlopen)

    with pytest.raises(
        wdi_client.WorldBankDataError, match="timed out after 5 seconds"
    ):
        wdi_client.fetch_json("https://example.test", timeout=5)


def test_fetch_json_wraps_invalid_json(monkeypatch) -> None:
    class FakeResponse:
        def __enter__(self) -> "FakeResponse":
            return self

        def __exit__(self, *args: object) -> None:
            return None

        def read(self) -> bytes:
            return b"not json"

    monkeypatch.setattr(wdi_client, "urlopen", lambda request, timeout: FakeResponse())

    with pytest.raises(wdi_client.WorldBankDataError, match="invalid JSON"):
        wdi_client.fetch_json("https://example.test", timeout=5)


def test_main_prints_population_json(monkeypatch, capsys) -> None:
    result = {
        "country": "JPN",
        "source": "World Bank World Development Indicators",
        "indicator": "SP.POP.TOTL",
        "indicator_name": "Population, total",
        "unit": "persons",
        "years": [{"year": 2025, "population": 123366734}],
    }

    def fake_get_population_data(country: str, *, years: int) -> dict[str, object]:
        assert country == "JPN"
        assert years == 1
        return result

    monkeypatch.setattr(indicators, "get_population_data", fake_get_population_data)

    assert app.main(["Population", "JPN", "--years", "1"]) == 0
    assert json.loads(capsys.readouterr().out) == result


def test_main_prints_gdp_json(monkeypatch, capsys) -> None:
    result = {
        "country": "JPN",
        "source": "World Bank World Development Indicators",
        "indicator": "NY.GDP.MKTP.CD",
        "indicator_name": "GDP (current US$)",
        "unit": "current US$",
        "years": [{"year": 2025, "gdp": 4200000000000.5}],
    }

    def fake_get_gdp_data(country: str, *, years: int) -> dict[str, object]:
        assert country == "JPN"
        assert years == 1
        return result

    monkeypatch.setattr(indicators, "get_gdp_data", fake_get_gdp_data)

    assert app.main(["GdP", "JPN", "--years", "1"]) == 0
    assert json.loads(capsys.readouterr().out) == result


def test_main_prints_gdp_per_capita_json(monkeypatch, capsys) -> None:
    result = {
        "country": "JPN",
        "source": "World Bank World Development Indicators",
        "indicator": "NY.GDP.PCAP.CD",
        "indicator_name": "GDP per capita (current US$)",
        "unit": "current US$",
        "years": [{"year": 2025, "gdp_per_capita": 33834.392}],
    }

    def fake_get_gdp_per_capita_data(
        country: str, *, years: int
    ) -> dict[str, object]:
        assert country == "JPN"
        assert years == 1
        return result

    monkeypatch.setattr(
        indicators, "get_gdp_per_capita_data", fake_get_gdp_per_capita_data
    )

    assert app.main(["GDP-Per-Capita", "JPN", "--years", "1"]) == 0
    assert json.loads(capsys.readouterr().out) == result


def test_main_prints_population_errors_to_stderr(monkeypatch, capsys) -> None:
    def fake_get_population_data(country: str, *, years: int) -> dict[str, object]:
        raise app.PopulationDataError("boom")

    monkeypatch.setattr(indicators, "get_population_data", fake_get_population_data)

    assert app.main(["population", "JPN"]) == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == "error: boom\n"


def test_main_prints_gdp_errors_to_stderr(monkeypatch, capsys) -> None:
    def fake_get_gdp_data(country: str, *, years: int) -> dict[str, object]:
        raise app.GdpDataError("boom")

    monkeypatch.setattr(indicators, "get_gdp_data", fake_get_gdp_data)

    assert app.main(["gdp", "JPN"]) == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == "error: boom\n"


def test_main_prints_gdp_per_capita_errors_to_stderr(monkeypatch, capsys) -> None:
    def fake_get_gdp_per_capita_data(
        country: str, *, years: int
    ) -> dict[str, object]:
        raise app.GdpPerCapitaDataError("boom")

    monkeypatch.setattr(
        indicators, "get_gdp_per_capita_data", fake_get_gdp_per_capita_data
    )

    assert app.main(["gdp-per-capita", "JPN"]) == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == "error: boom\n"


def test_main_requires_indicator(capsys) -> None:
    with pytest.raises(SystemExit) as exc_info:
        app.main([])

    assert exc_info.value.code == 2
    captured = capsys.readouterr()
    assert "the following arguments are required: indicator, country" in captured.err
