"""Tests for strategy analysis module."""

import pytest
from dataclasses import asdict

from src.analysis.strategy import (
    PitStop,
    TyreStint,
    DriverStrategy,
    format_strategy_report,
)


class TestPitStop:
    """Tests for PitStop dataclass."""

    def test_position_change_gained(self):
        """Test position change when positions gained."""
        ps = PitStop(
            lap=15,
            duration=2.5,
            position_before=5,
            position_after=3,
            tyre_from="SOFT",
            tyre_to="MEDIUM",
        )
        assert ps.position_change == -2  # Gained 2 positions

    def test_position_change_lost(self):
        """Test position change when positions lost."""
        ps = PitStop(
            lap=20,
            duration=3.0,
            position_before=3,
            position_after=6,
            tyre_from="MEDIUM",
            tyre_to="HARD",
        )
        assert ps.position_change == 3  # Lost 3 positions

    def test_position_change_none(self):
        """Test position change when positions unknown."""
        ps = PitStop(
            lap=10,
            duration=2.5,
            position_before=None,
            position_after=None,
            tyre_from="SOFT",
            tyre_to="MEDIUM",
        )
        assert ps.position_change == 0


class TestTyreStint:
    """Tests for TyreStint dataclass."""

    def test_compound_short_soft(self):
        stint = TyreStint(
            compound="SOFT",
            start_lap=1,
            end_lap=15,
            laps=15,
            avg_lap_time=90.5,
            best_lap_time=89.2,
            degradation=0.05,
        )
        assert stint.compound_short == "S"

    def test_compound_short_medium(self):
        stint = TyreStint(
            compound="MEDIUM",
            start_lap=16,
            end_lap=35,
            laps=20,
            avg_lap_time=91.0,
            best_lap_time=90.1,
            degradation=0.03,
        )
        assert stint.compound_short == "M"

    def test_compound_short_hard(self):
        stint = TyreStint(
            compound="HARD",
            start_lap=36,
            end_lap=57,
            laps=22,
            avg_lap_time=92.0,
            best_lap_time=91.5,
            degradation=0.02,
        )
        assert stint.compound_short == "H"

    def test_compound_short_empty(self):
        stint = TyreStint(
            compound="",
            start_lap=1,
            end_lap=1,
            laps=1,
            avg_lap_time=None,
            best_lap_time=None,
            degradation=None,
        )
        assert stint.compound_short == "?"


class TestDriverStrategy:
    """Tests for DriverStrategy dataclass."""

    def test_num_stops(self):
        strategy = DriverStrategy(
            driver_code="VER",
            driver_name="Max Verstappen",
            finish_position=1,
            start_position=1,
            pit_stops=[
                PitStop(15, 2.5, 1, 2, "SOFT", "MEDIUM"),
                PitStop(35, 2.4, 1, 1, "MEDIUM", "HARD"),
            ],
        )
        assert strategy.num_stops == 2

    def test_strategy_string(self):
        strategy = DriverStrategy(
            driver_code="HAM",
            driver_name="Lewis Hamilton",
            finish_position=2,
            start_position=3,
            stints=[
                TyreStint("SOFT", 1, 15, 15, 90.0, 89.0, 0.05),
                TyreStint("MEDIUM", 16, 35, 20, 91.0, 90.0, 0.03),
                TyreStint("HARD", 36, 57, 22, 92.0, 91.0, 0.02),
            ],
        )
        assert strategy.strategy_string == "S-M-H"

    def test_strategy_string_empty(self):
        strategy = DriverStrategy(
            driver_code="DNF",
            driver_name="Driver DNF",
            finish_position=None,
            start_position=10,
        )
        assert strategy.strategy_string == "N/A"

    def test_position_change_gained(self):
        strategy = DriverStrategy(
            driver_code="ALO",
            driver_name="Fernando Alonso",
            finish_position=3,
            start_position=8,
        )
        assert strategy.position_change == 5  # Gained 5 positions

    def test_position_change_lost(self):
        strategy = DriverStrategy(
            driver_code="PER",
            driver_name="Sergio Perez",
            finish_position=8,
            start_position=2,
        )
        assert strategy.position_change == -6  # Lost 6 positions


class TestFormatStrategyReport:
    """Tests for format_strategy_report function."""

    def test_basic_report(self):
        strategies = [
            DriverStrategy(
                driver_code="VER",
                driver_name="Max Verstappen",
                finish_position=1,
                start_position=1,
                pit_stops=[PitStop(15, 2.5, 1, 1, "SOFT", "MEDIUM")],
                stints=[
                    TyreStint("SOFT", 1, 15, 15, 90.0, 89.0, 0.05),
                    TyreStint("MEDIUM", 16, 57, 42, 91.0, 90.0, 0.03),
                ],
                total_pit_time=2.5,
                positions_lost_in_pits=0,
            ),
        ]

        report = format_strategy_report(strategies, "Monaco Grand Prix")

        assert "STRATEGY ANALYSIS" in report
        assert "Monaco Grand Prix" in report
        assert "VER" in report
        assert "S-M" in report

    def test_empty_strategies(self):
        report = format_strategy_report([], "Test GP")
        assert "STRATEGY ANALYSIS" in report
