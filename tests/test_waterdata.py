import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from waterdata import (  # noqa: E402
    default_window,
    latest_with_delta,
    normalize_headers,
    out_of_range,
    prepare_data,
    rows_to_frame,
    worksheet_gid,
)


def test_headers_follow_namedtuple_rename_rule():
    from collections import namedtuple

    headers = ["Timestamp", "Temperature", "EC (uS/cm)", "pH", "Water Level", "Light", "Light %", "pH", "class", ""]
    assert normalize_headers(headers) == list(namedtuple("Row", headers, rename=True)._fields)


def test_rows_to_frame_maps_sheet_values_to_expected_columns():
    values = [
        ["Timestamp", "Temperature", "EC (uS/cm)", "pH", "Water Level", "Light", "Light %"],
        ["2025-01-01 09:00:00", "20.5", "1,200.5", "6.5", "12", "0.4", "40"],
        ["", "", "", "", "", "", ""],
        ["2025-01-01 10:00:00", "21", "1100"],
    ]
    df = prepare_data(rows_to_frame(values))
    assert list(df.columns) == ["Timestamp", "Temperature", "EC", "pH", "WaterLevel", "Light", "LightPercentage"]
    assert len(df) == 2
    assert df["EC"].tolist() == [1200.5, 1100.0]
    assert df["pH"].isna().tolist() == [False, True]


def test_worksheet_gid_parsing():
    assert worksheet_gid("https://docs.google.com/spreadsheets/d/abc/edit#gid=123") == 123
    assert worksheet_gid("https://docs.google.com/spreadsheets/d/abc/edit?gid=7") == 7
    assert worksheet_gid("https://docs.google.com/spreadsheets/d/abc/edit") is None


def raw_frame():
    return pd.DataFrame(
        {
            "Timestamp": ["2025-01-01 10:00:00", "2025-01-01 09:00:00", "2025-01-01 11:00:00"],
            "Temperature": [21.234, 20.0, 35.555],
            "_2": ["800.12345", "790", "810"],
            "pH": [6.5, 6.4, 8.2],
            "_4": [12, 11, 10],
            "Light": [0.5, 0.4, 0.6],
            "_6": [50.123, 40, 60],
        }
    )


def test_prepare_renames_sorts_and_rounds():
    df = prepare_data(raw_frame())
    assert {"EC", "WaterLevel", "LightPercentage"} <= set(df.columns)
    assert df["Timestamp"].is_monotonic_increasing
    assert df["EC"].iloc[1] == 800.1235
    assert df["Temperature"].iloc[1] == 21.23


def test_unparseable_timestamps_are_left_untouched():
    raw = raw_frame()
    raw["Timestamp"] = ["a", "b", "c"]
    df = prepare_data(raw)
    assert len(df) == 3
    assert list(df["Timestamp"]) == ["a", "b", "c"]


def test_default_window_never_goes_below_one():
    assert default_window(100) == (1, 100)
    assert default_window(8000) == (3000, 8000)


def test_latest_with_delta():
    df = prepare_data(raw_frame())
    latest, delta = latest_with_delta(df, "WaterLevel")
    assert latest == 10 and delta == -2
    assert latest_with_delta(df, "Missing") == (None, None)


def test_out_of_range_flags_latest_values():
    df = prepare_data(raw_frame())
    warnings = out_of_range(df, {"Temperature": (15, 30), "pH": (5.5, 7.5), "EC": (200, 1400)})
    assert any("Temperature is high" in w for w in warnings)
    assert any("pH is high" in w for w in warnings)
    assert not any(w.startswith("EC") for w in warnings)
