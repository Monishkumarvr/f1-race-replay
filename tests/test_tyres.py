"""Tests for src/lib/tyres.py utility functions."""

import pytest
from src.lib.tyres import get_tyre_compound_int, get_tyre_compound_str


class TestGetTyreCompoundInt:
    """Tests for get_tyre_compound_int function."""

    def test_soft_compound(self):
        assert get_tyre_compound_int("SOFT") == 0

    def test_medium_compound(self):
        assert get_tyre_compound_int("MEDIUM") == 1

    def test_hard_compound(self):
        assert get_tyre_compound_int("HARD") == 2

    def test_intermediate_compound(self):
        assert get_tyre_compound_int("INTERMEDIATE") == 3

    def test_wet_compound(self):
        assert get_tyre_compound_int("WET") == 4

    def test_lowercase_input(self):
        """Test that lowercase input is handled correctly."""
        assert get_tyre_compound_int("soft") == 0
        assert get_tyre_compound_int("medium") == 1

    def test_mixed_case_input(self):
        """Test that mixed case input is handled correctly."""
        assert get_tyre_compound_int("Soft") == 0
        assert get_tyre_compound_int("MEDIUM") == 1

    def test_unknown_compound(self):
        """Test that unknown compound returns -1."""
        assert get_tyre_compound_int("UNKNOWN") == -1
        assert get_tyre_compound_int("SUPER_SOFT") == -1
        assert get_tyre_compound_int("") == -1


class TestGetTyreCompoundStr:
    """Tests for get_tyre_compound_str function."""

    def test_soft_int(self):
        assert get_tyre_compound_str(0) == "SOFT"

    def test_medium_int(self):
        assert get_tyre_compound_str(1) == "MEDIUM"

    def test_hard_int(self):
        assert get_tyre_compound_str(2) == "HARD"

    def test_intermediate_int(self):
        assert get_tyre_compound_str(3) == "INTERMEDIATE"

    def test_wet_int(self):
        assert get_tyre_compound_str(4) == "WET"

    def test_invalid_int_negative(self):
        """Test that invalid negative int returns UNKNOWN."""
        assert get_tyre_compound_str(-1) == "UNKNOWN"

    def test_invalid_int_large(self):
        """Test that invalid large int returns UNKNOWN."""
        assert get_tyre_compound_str(99) == "UNKNOWN"


class TestRoundTrip:
    """Test round-trip conversion between int and string."""

    def test_all_compounds_roundtrip(self):
        """Test that converting to int and back gives original string."""
        compounds = ["SOFT", "MEDIUM", "HARD", "INTERMEDIATE", "WET"]
        for compound in compounds:
            compound_int = get_tyre_compound_int(compound)
            result = get_tyre_compound_str(compound_int)
            assert result == compound
