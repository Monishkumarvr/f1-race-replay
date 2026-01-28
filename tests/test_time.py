import pytest
from src.lib.time import format_time, parse_time_string


class TestFormatTime:
    def test_zero_seconds(self):
        assert format_time(0) == "00:00.000"

    def test_simple_seconds(self):
        assert format_time(30.5) == "00:30.500"

    def test_minutes_and_seconds(self):
        assert format_time(90.123) == "01:30.123"

    def test_large_value(self):
        assert format_time(3661.5) == "61:01.500"

    def test_none_input(self):
        assert format_time(None) == "N/A"

    def test_negative_input(self):
        assert format_time(-1) == "N/A"

    def test_sub_millisecond_rounding(self):
        result = format_time(60.1234)
        assert result == "01:00.123"


class TestParseTimeString:
    def test_four_part_format(self):
        # "00:01:26:123000" -> 86.123 seconds
        result = parse_time_string("00:01:26:123000")
        assert result == 86.123

    def test_four_part_with_dot(self):
        # "00:01:26.123000"
        result = parse_time_string("00:01:26.123000")
        assert result == 86.123

    def test_three_part_mm_ss_micro(self):
        # "01:26.123000" -> last part has > 2 digits, treated as microseconds
        result = parse_time_string("01:26.123000")
        assert result == 86.123

    def test_three_part_hh_mm_ss(self):
        # "01:26:30" -> last part has <= 2 digits, treated as HH:MM:SS
        result = parse_time_string("01:26:30")
        assert result == 5190.0

    def test_two_part_mm_ss(self):
        # "01:26" -> 86 seconds
        result = parse_time_string("01:26")
        assert result == 86.0

    def test_timedelta_format(self):
        # "0 days 00:01:27.060000"
        result = parse_time_string("0 days 00:01:27.060000")
        assert result == 87.06

    def test_none_input(self):
        result = parse_time_string(None)
        assert result is None

    def test_empty_string(self):
        result = parse_time_string("")
        assert result is None

    def test_invalid_string(self):
        result = parse_time_string("invalid")
        assert result is None

    def test_typical_f1_lap_time(self):
        # Typical F1 lap: 1:26.123
        result = parse_time_string("01:26.123000")
        assert result == 86.123

    def test_trailing_text_stripped(self):
        # Input with trailing text after space
        result = parse_time_string("01:26.123000 extra")
        assert result == 86.123

    def test_whitespace_in_value(self):
        # Leading whitespace before colon-separated time gets split on space first,
        # so only trailing whitespace after the time value is handled
        result = parse_time_string("01:26 ")
        assert result == 86.0
