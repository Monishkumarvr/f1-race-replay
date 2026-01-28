"""Pytest configuration and shared fixtures for F1 Race Replay tests."""

import pytest


@pytest.fixture
def sample_time_strings():
    """Sample time strings for testing parse_time_string."""
    return {
        "four_part": "00:01:26:123000",
        "four_part_dot": "00:01:26.123000",
        "three_part_micro": "01:26.123000",
        "three_part_hms": "01:26:30",
        "two_part": "01:26",
        "timedelta_format": "0 days 00:01:27.060000",
        "invalid": "invalid",
        "empty": "",
    }


@pytest.fixture
def tyre_compounds():
    """All valid F1 tyre compounds."""
    return ["SOFT", "MEDIUM", "HARD", "INTERMEDIATE", "WET"]


@pytest.fixture
def sample_lap_times():
    """Sample F1 lap times in seconds for testing."""
    return {
        "fast_lap": 86.123,  # 1:26.123
        "slow_lap": 92.456,  # 1:32.456
        "out_lap": 120.5,    # 2:00.5
        "invalid": -1.0,
    }
