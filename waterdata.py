"""Data preparation helpers for the Water Data dashboard (no Streamlit dependency)."""

from __future__ import annotations

import keyword
import re
from urllib.parse import parse_qs, urlparse

import pandas as pd

# Headers that are not valid identifiers become "_<position>" (the namedtuple rename rule the
# original gsheetsdb version relied on); these map them back to readable names.
COLUMN_RENAMES = {"_2": "EC", "_4": "WaterLevel", "_6": "LightPercentage"}
ROUNDING = {"Temperature": 2, "EC": 4, "pH": 4, "Light": 4, "LightPercentage": 2, "WaterLevel": 2}
NUMERIC_COLUMNS = list(ROUNDING)

DEFAULT_THRESHOLDS = {
    "Temperature": (15.0, 30.0),
    "pH": (5.5, 7.5),
    "EC": (200.0, 1400.0),
}


def normalize_headers(headers: list[str]) -> list[str]:
    seen: set[str] = set()
    names = []
    for index, header in enumerate(headers):
        name = str(header).strip()
        if not name.isidentifier() or keyword.iskeyword(name) or name.startswith("_") or name in seen:
            name = f"_{index}"
        seen.add(name)
        names.append(name)
    return names


def rows_to_frame(values: list[list[str]]) -> pd.DataFrame:
    """Turn a worksheet's values (header row first) into a DataFrame."""
    if not values:
        return pd.DataFrame()
    headers = normalize_headers(values[0])
    width = len(headers)
    rows = [(row + [""] * width)[:width] for row in values[1:] if any(str(cell).strip() for cell in row)]
    return pd.DataFrame(rows, columns=headers)


def worksheet_gid(sheet_url: str) -> int | None:
    parsed = urlparse(sheet_url)
    for part in (parsed.fragment, parsed.query):
        gid = parse_qs(part).get("gid")
        if gid and gid[0].isdigit():
            return int(gid[0])
    return None


def _to_number(series: pd.Series) -> pd.Series:
    if not pd.api.types.is_numeric_dtype(series):
        series = series.astype(str).str.replace(",", "", regex=False).str.strip()
    return pd.to_numeric(series, errors="coerce")


def prepare_data(raw: pd.DataFrame) -> pd.DataFrame:
    df = raw.rename(columns=COLUMN_RENAMES).copy()
    if "Timestamp" in df.columns:
        parsed = pd.to_datetime(df["Timestamp"], errors="coerce")
        # Only switch to datetimes when the column really is timestamps, so odd formats never wipe the data.
        if len(parsed) and parsed.notna().mean() >= 0.9:
            df["Timestamp"] = parsed
            df = df.dropna(subset=["Timestamp"]).sort_values("Timestamp", kind="stable")
    for column in NUMERIC_COLUMNS:
        if column in df.columns:
            df[column] = _to_number(df[column]).round(ROUNDING[column])
    return df.reset_index(drop=True)


def default_window(length: int, size: int = 5000) -> tuple[int, int]:
    """Slider bounds (1-based start, end) covering the most recent ``size`` rows."""
    return max(1, length - size), length


def latest_with_delta(df: pd.DataFrame, column: str) -> tuple[float | None, float | None]:
    values = df[column].dropna() if column in df.columns else pd.Series(dtype=float)
    if values.empty:
        return None, None
    latest = float(values.iloc[-1])
    delta = latest - float(values.iloc[-2]) if len(values) > 1 else None
    return latest, delta


def out_of_range(df: pd.DataFrame, thresholds: dict[str, tuple[float, float]]) -> list[str]:
    """Return warnings for the latest reading of each monitored column outside its range."""
    warnings = []
    for column, (low, high) in thresholds.items():
        latest, _ = latest_with_delta(df, column)
        if latest is None:
            continue
        if latest < low:
            warnings.append(f"{column} is low: {latest:g} (min {low:g})")
        elif latest > high:
            warnings.append(f"{column} is high: {latest:g} (max {high:g})")
    return warnings
