"""Tests for f1_data.py utility functions."""

import pytest
import pandas as pd
import numpy as np

# Skip all tests in this module if fastf1 is not available
pytest.importorskip("fastf1")

from src.f1_data import _convert_time_to_seconds


class TestConvertTimeToSeconds:
    """Tests for _convert_time_to_seconds helper function."""

    def test_valid_timedelta(self):
        """Test conversion of a valid Timedelta."""
        td = pd.Timedelta(seconds=86.123)
        result = _convert_time_to_seconds(td)
        assert result == "86.123"

    def test_timedelta_with_minutes(self):
        """Test conversion of a Timedelta with minutes."""
        td = pd.Timedelta(minutes=1, seconds=26, milliseconds=123)
        result = _convert_time_to_seconds(td)
        assert result == "86.123"

    def test_nat_returns_none(self):
        """Test that NaT (Not a Time) returns None."""
        result = _convert_time_to_seconds(pd.NaT)
        assert result is None

    def test_none_returns_none(self):
        """Test that None input returns None."""
        result = _convert_time_to_seconds(None)
        assert result is None

    def test_zero_timedelta(self):
        """Test conversion of zero Timedelta."""
        td = pd.Timedelta(seconds=0)
        result = _convert_time_to_seconds(td)
        assert result == "0.0"

    def test_large_timedelta(self):
        """Test conversion of a large Timedelta (hours)."""
        td = pd.Timedelta(hours=1, minutes=30, seconds=45)
        result = _convert_time_to_seconds(td)
        assert result == "5445.0"

    def test_microsecond_precision(self):
        """Test that microseconds are preserved."""
        td = pd.Timedelta(seconds=1, microseconds=123456)
        result = _convert_time_to_seconds(td)
        assert result == "1.123456"


class TestResampleWeatherData:
    """Tests for _resample_weather_data helper function.

    Note: These tests use mocked session objects since we can't easily
    create real FastF1 session objects in unit tests.
    """

    def test_none_weather_data_returns_none(self):
        """Test that a session with no weather_data returns None."""
        from src.f1_data import _resample_weather_data

        class MockSession:
            weather_data = None

        result = _resample_weather_data(MockSession(), np.array([0, 1, 2]), 0.0)
        assert result is None

    def test_empty_weather_data_returns_none(self):
        """Test that a session with empty weather_data returns None."""
        from src.f1_data import _resample_weather_data

        class MockSession:
            weather_data = pd.DataFrame()

        result = _resample_weather_data(MockSession(), np.array([0, 1, 2]), 0.0)
        assert result is None

    def test_valid_weather_data_resamples(self):
        """Test that valid weather data is properly resampled."""
        from src.f1_data import _resample_weather_data

        # Create mock weather DataFrame
        weather_df = pd.DataFrame({
            "Time": pd.to_timedelta([0, 10, 20], unit="s"),
            "TrackTemp": [30.0, 32.0, 34.0],
            "AirTemp": [25.0, 26.0, 27.0],
            "Humidity": [50.0, 52.0, 54.0],
            "WindSpeed": [5.0, 6.0, 7.0],
            "WindDirection": [180.0, 185.0, 190.0],
            "Rainfall": [False, False, True],
        })

        class MockSession:
            pass

        mock_session = MockSession()
        mock_session.weather_data = weather_df

        timeline = np.array([0.0, 5.0, 10.0, 15.0, 20.0])
        result = _resample_weather_data(mock_session, timeline, global_t_min=0.0)

        assert result is not None
        assert "track_temp" in result
        assert "air_temp" in result
        assert "humidity" in result
        assert "wind_speed" in result
        assert "wind_direction" in result
        assert "rainfall" in result

        # Check interpolated values at midpoint (t=10s)
        assert result["track_temp"][2] == pytest.approx(32.0, rel=0.01)
        assert result["air_temp"][2] == pytest.approx(26.0, rel=0.01)
