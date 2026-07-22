from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

BASE_URL = "https://api.worldbank.org/v2"
DEFAULT_TIMEOUT_SECONDS = 30


class WorldBankDataError(RuntimeError):
    """Raised when World Bank data cannot be fetched or parsed."""


def normalize_iso3(country: str) -> str:
    iso3 = country.strip().upper()
    if not re.fullmatch(r"[A-Z]{3}", iso3):
        raise ValueError("country must be an ISO 3166 alpha-3 code, e.g. JPN")
    return iso3


def fetch_indicator_rows(
    iso3_codes: list[str],
    *,
    indicator: str,
    years: int,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
) -> list[dict[str, Any]]:
    countries = ";".join(iso3_codes)
    start_year, end_year = year_range_for_recent_values(years)
    year_count = end_year - start_year + 1
    per_page = max(year_count * len(iso3_codes), year_count)
    params = urlencode(
        {
            "format": "json",
            "date": f"{start_year}:{end_year}",
            "per_page": per_page,
        }
    )
    url = f"{BASE_URL}/country/{countries}/indicator/{indicator}?{params}"
    return payload_rows(fetch_json(url, timeout=timeout))


def fetch_json(url: str, *, timeout: int) -> Any:
    request = Request(
        url,
        headers={"Accept": "application/json"},
    )

    try:
        with urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except TimeoutError as exc:
        raise WorldBankDataError(
            f"World Bank API request timed out after {timeout} seconds"
        ) from exc
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise WorldBankDataError(
            f"World Bank API request failed with HTTP {exc.code}: {detail}"
        ) from exc
    except URLError as exc:
        raise WorldBankDataError(
            f"World Bank API request failed: {exc.reason}"
        ) from exc
    except json.JSONDecodeError as exc:
        raise WorldBankDataError("World Bank API returned invalid JSON") from exc

    return payload


def payload_rows(payload: Any) -> list[dict[str, Any]]:
    if not isinstance(payload, list) or len(payload) != 2:
        raise WorldBankDataError(
            "World Bank API returned an unexpected response shape"
        )

    metadata, rows = payload
    if isinstance(metadata, dict) and "message" in metadata:
        raise WorldBankDataError(format_world_bank_error(metadata["message"]))
    if not isinstance(rows, list):
        raise WorldBankDataError("World Bank API returned an unexpected data shape")
    return rows


def select_recent_indicator_values(
    rows: list[dict[str, Any]],
    *,
    years: int,
    value_key: str,
) -> list[dict[str, int | float]]:
    parsed: dict[int, int | float] = {}
    for row in rows:
        year = first_int(row, "date")
        value = first_float(row, "value")
        if year is None or value is None:
            continue
        parsed[year] = value

    return [
        {"year": year, value_key: parsed[year]}
        for year in sorted(parsed)[-years:]
    ]


def format_world_bank_error(message: Any) -> str:
    if isinstance(message, list):
        parts = []
        for item in message:
            if isinstance(item, dict):
                key = item.get("key")
                value = item.get("value")
                parts.append(": ".join(str(part) for part in (key, value) if part))
        if parts:
            return "; ".join(parts)
    return "World Bank API returned an error"


def year_range_for_recent_values(years: int) -> tuple[int, int]:
    end_year = datetime.now(timezone.utc).year
    start_year = end_year - years
    return start_year, end_year


def row_country_iso3(row: dict[str, Any]) -> str | None:
    countryiso3code = row.get("countryiso3code")
    if isinstance(countryiso3code, str) and countryiso3code:
        return countryiso3code.upper()

    country = row.get("country")
    if isinstance(country, dict):
        country_id = country.get("id")
        if isinstance(country_id, str) and len(country_id) == 3:
            return country_id.upper()

    return None


def first_int(row: dict[str, Any], *keys: str) -> int | None:
    for key in keys:
        value = row.get(key)
        if value is None:
            continue
        try:
            return int(value)
        except (TypeError, ValueError):
            continue
    return None


def first_float(row: dict[str, Any], *keys: str) -> float | None:
    for key in keys:
        value = row.get(key)
        if value is None:
            continue
        try:
            return float(value)
        except (TypeError, ValueError):
            continue
    return None
