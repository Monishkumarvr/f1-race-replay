"""Post-race strategy analysis module.

Provides functions to analyze pit stop strategies, tyre usage,
and race pace from FastF1 session data.
"""

import logging
from dataclasses import dataclass, field
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class PitStop:
    """Represents a single pit stop."""
    lap: int
    duration: float  # seconds
    position_before: Optional[int]
    position_after: Optional[int]
    tyre_from: str
    tyre_to: str

    @property
    def position_change(self) -> int:
        """Positions gained (negative) or lost (positive) due to pit stop."""
        if self.position_before is None or self.position_after is None:
            return 0
        return self.position_after - self.position_before


@dataclass
class TyreStint:
    """Represents a stint on a single tyre compound."""
    compound: str
    start_lap: int
    end_lap: int
    laps: int
    avg_lap_time: Optional[float]  # seconds
    best_lap_time: Optional[float]  # seconds
    degradation: Optional[float]  # seconds per lap (positive = slower)

    @property
    def compound_short(self) -> str:
        """Get short compound name (S/M/H/I/W)."""
        return self.compound[0] if self.compound else "?"


@dataclass
class DriverStrategy:
    """Complete strategy analysis for a driver."""
    driver_code: str
    driver_name: str
    finish_position: Optional[int]
    start_position: Optional[int]
    pit_stops: list[PitStop] = field(default_factory=list)
    stints: list[TyreStint] = field(default_factory=list)
    total_pit_time: float = 0.0
    positions_lost_in_pits: int = 0

    @property
    def num_stops(self) -> int:
        return len(self.pit_stops)

    @property
    def strategy_string(self) -> str:
        """Get strategy as string like 'S-M-H' for tyres used."""
        if not self.stints:
            return "N/A"
        return "-".join(s.compound_short for s in self.stints)

    @property
    def position_change(self) -> int:
        """Total positions gained (positive) or lost (negative)."""
        if self.start_position is None or self.finish_position is None:
            return 0
        return self.start_position - self.finish_position


def get_pit_stops(session, driver_code: str) -> list[PitStop]:
    """Extract pit stop data for a driver from session laps.

    Args:
        session: FastF1 session object (loaded with laps)
        driver_code: Driver abbreviation (e.g., 'VER', 'HAM')

    Returns:
        List of PitStop objects
    """
    pit_stops = []

    try:
        driver_laps = session.laps.pick_drivers(driver_code)
        if driver_laps.empty:
            return pit_stops

        # Find laps where a pit stop occurred (PitOutTime is not NaT)
        for i, (_, lap) in enumerate(driver_laps.iterrows()):
            if pd.notna(lap.get("PitInTime")):
                # This lap had a pit entry
                pit_in_lap = int(lap["LapNumber"])

                # Get pit duration
                pit_duration = 0.0
                if pd.notna(lap.get("PitOutTime")) and pd.notna(lap.get("PitInTime")):
                    pit_duration = (lap["PitOutTime"] - lap["PitInTime"]).total_seconds()

                # Get position before/after
                pos_before = int(lap["Position"]) if pd.notna(lap.get("Position")) else None

                # Find next lap to get position after pit
                next_laps = driver_laps[driver_laps["LapNumber"] > pit_in_lap]
                pos_after = None
                if not next_laps.empty:
                    next_lap = next_laps.iloc[0]
                    pos_after = int(next_lap["Position"]) if pd.notna(next_lap.get("Position")) else None

                # Get tyre compounds
                tyre_from = str(lap.get("Compound", "UNKNOWN"))
                tyre_to = tyre_from  # Will be updated from next lap
                if not next_laps.empty:
                    tyre_to = str(next_laps.iloc[0].get("Compound", "UNKNOWN"))

                pit_stops.append(PitStop(
                    lap=pit_in_lap,
                    duration=round(pit_duration, 3),
                    position_before=pos_before,
                    position_after=pos_after,
                    tyre_from=tyre_from,
                    tyre_to=tyre_to,
                ))

    except Exception as e:
        logger.warning("Error extracting pit stops for %s: %s", driver_code, e)

    return pit_stops


def get_tyre_stints(session, driver_code: str) -> list[TyreStint]:
    """Extract tyre stint data for a driver.

    Args:
        session: FastF1 session object
        driver_code: Driver abbreviation

    Returns:
        List of TyreStint objects
    """
    stints = []

    try:
        driver_laps = session.laps.pick_drivers(driver_code)
        if driver_laps.empty:
            return stints

        # Group laps by stint number
        if "Stint" not in driver_laps.columns:
            # Fallback: group by compound changes
            current_compound = None
            stint_laps = []

            for _, lap in driver_laps.iterrows():
                compound = str(lap.get("Compound", "UNKNOWN"))
                if compound != current_compound:
                    if stint_laps and current_compound:
                        stints.append(_create_stint(stint_laps, current_compound))
                    current_compound = compound
                    stint_laps = [lap]
                else:
                    stint_laps.append(lap)

            # Don't forget last stint
            if stint_laps and current_compound:
                stints.append(_create_stint(stint_laps, current_compound))
        else:
            # Use stint numbers from FastF1
            for stint_num in driver_laps["Stint"].unique():
                stint_laps = driver_laps[driver_laps["Stint"] == stint_num]
                if stint_laps.empty:
                    continue

                compound = str(stint_laps.iloc[0].get("Compound", "UNKNOWN"))
                stints.append(_create_stint(stint_laps.to_dict('records'), compound))

    except Exception as e:
        logger.warning("Error extracting stints for %s: %s", driver_code, e)

    return stints


def _create_stint(laps: list, compound: str) -> TyreStint:
    """Create a TyreStint from a list of lap data."""
    if not laps:
        return TyreStint(
            compound=compound,
            start_lap=0,
            end_lap=0,
            laps=0,
            avg_lap_time=None,
            best_lap_time=None,
            degradation=None,
        )

    # Handle both DataFrame rows and dicts
    def get_val(lap, key, default=None):
        if hasattr(lap, 'get'):
            return lap.get(key, default)
        return getattr(lap, key, default)

    lap_numbers = [int(get_val(lap, "LapNumber", 0)) for lap in laps]
    start_lap = min(lap_numbers) if lap_numbers else 0
    end_lap = max(lap_numbers) if lap_numbers else 0

    # Calculate lap times (filter out outliers like pit laps)
    lap_times = []
    for lap in laps:
        lt = get_val(lap, "LapTime")
        if pd.notna(lt):
            try:
                secs = lt.total_seconds() if hasattr(lt, 'total_seconds') else float(lt)
                # Filter out obvious pit laps (> 2 minutes)
                if secs < 120:
                    lap_times.append(secs)
            except (ValueError, TypeError):
                pass

    avg_time = sum(lap_times) / len(lap_times) if lap_times else None
    best_time = min(lap_times) if lap_times else None

    # Calculate degradation (simple linear regression)
    degradation = None
    if len(lap_times) >= 3:
        try:
            # Compare first third vs last third average
            third = len(lap_times) // 3
            if third > 0:
                early_avg = sum(lap_times[:third]) / third
                late_avg = sum(lap_times[-third:]) / third
                laps_between = len(lap_times) - third
                if laps_between > 0:
                    degradation = round((late_avg - early_avg) / laps_between, 3)
        except Exception:
            pass

    return TyreStint(
        compound=compound,
        start_lap=start_lap,
        end_lap=end_lap,
        laps=len(laps),
        avg_lap_time=round(avg_time, 3) if avg_time else None,
        best_lap_time=round(best_time, 3) if best_time else None,
        degradation=degradation,
    )


def analyze_race_strategy(session) -> list[DriverStrategy]:
    """Perform complete strategy analysis for all drivers in a session.

    Args:
        session: FastF1 session object (must be loaded with laps)

    Returns:
        List of DriverStrategy objects, sorted by finish position
    """
    strategies = []

    try:
        results = session.results
        if results is None or results.empty:
            logger.warning("No results data available")
            return strategies

        for _, driver in results.iterrows():
            driver_code = driver.get("Abbreviation", "")
            if not driver_code:
                continue

            driver_name = driver.get("FullName", driver_code)
            finish_pos = int(driver["Position"]) if pd.notna(driver.get("Position")) else None
            grid_pos = int(driver["GridPosition"]) if pd.notna(driver.get("GridPosition")) else None

            pit_stops = get_pit_stops(session, driver_code)
            stints = get_tyre_stints(session, driver_code)

            total_pit_time = sum(ps.duration for ps in pit_stops)
            positions_lost = sum(ps.position_change for ps in pit_stops)

            strategies.append(DriverStrategy(
                driver_code=driver_code,
                driver_name=driver_name,
                finish_position=finish_pos,
                start_position=grid_pos,
                pit_stops=pit_stops,
                stints=stints,
                total_pit_time=round(total_pit_time, 3),
                positions_lost_in_pits=positions_lost,
            ))

        # Sort by finish position
        strategies.sort(key=lambda s: s.finish_position or 999)

    except Exception as e:
        logger.error("Error analyzing race strategy: %s", e)

    return strategies


def format_strategy_report(strategies: list[DriverStrategy], event_name: str = "") -> str:
    """Format strategy analysis as a human-readable report.

    Args:
        strategies: List of DriverStrategy objects
        event_name: Optional event name for header

    Returns:
        Formatted string report
    """
    lines = []

    # Header
    if event_name:
        lines.append(f"{'=' * 60}")
        lines.append(f"STRATEGY ANALYSIS: {event_name}")
        lines.append(f"{'=' * 60}")
    else:
        lines.append("RACE STRATEGY ANALYSIS")
        lines.append("=" * 40)

    lines.append("")

    # Summary table header
    lines.append(f"{'Pos':<4} {'Driver':<20} {'Strategy':<12} {'Stops':<6} {'Pit Time':<10} {'Gained':<6}")
    lines.append("-" * 60)

    for strat in strategies:
        pos = str(strat.finish_position) if strat.finish_position else "DNF"
        gained = f"{strat.position_change:+d}" if strat.position_change != 0 else "0"
        pit_time = f"{strat.total_pit_time:.1f}s" if strat.total_pit_time else "N/A"

        lines.append(
            f"{pos:<4} {strat.driver_code:<20} {strat.strategy_string:<12} "
            f"{strat.num_stops:<6} {pit_time:<10} {gained:<6}"
        )

    lines.append("")
    lines.append("-" * 60)

    # Detailed stint analysis for top 5
    lines.append("")
    lines.append("STINT DETAILS (Top 5)")
    lines.append("-" * 40)

    for strat in strategies[:5]:
        if not strat.stints:
            continue

        lines.append(f"\n{strat.driver_code} ({strat.driver_name}):")
        for i, stint in enumerate(strat.stints, 1):
            avg = f"{stint.avg_lap_time:.3f}s" if stint.avg_lap_time else "N/A"
            best = f"{stint.best_lap_time:.3f}s" if stint.best_lap_time else "N/A"
            deg = f"{stint.degradation:+.3f}s/lap" if stint.degradation else "N/A"

            lines.append(
                f"  Stint {i}: {stint.compound:<12} "
                f"Laps {stint.start_lap}-{stint.end_lap} ({stint.laps} laps) | "
                f"Avg: {avg} | Best: {best} | Deg: {deg}"
            )

    # Pit stop details
    lines.append("")
    lines.append("PIT STOP ANALYSIS")
    lines.append("-" * 40)

    # Find notable pit stops
    all_stops = [(s.driver_code, ps) for s in strategies for ps in s.pit_stops]

    if all_stops:
        # Fastest pit stop
        fastest = min(all_stops, key=lambda x: x[1].duration if x[1].duration > 0 else 999)
        lines.append(f"Fastest pit stop: {fastest[0]} - {fastest[1].duration:.3f}s (Lap {fastest[1].lap})")

        # Slowest pit stop (excluding > 30s which might be penalties/issues)
        normal_stops = [(d, ps) for d, ps in all_stops if 0 < ps.duration < 30]
        if normal_stops:
            slowest = max(normal_stops, key=lambda x: x[1].duration)
            lines.append(f"Slowest pit stop: {slowest[0]} - {slowest[1].duration:.3f}s (Lap {slowest[1].lap})")

        # Most positions lost in single stop
        worst_loss = max(all_stops, key=lambda x: x[1].position_change)
        if worst_loss[1].position_change > 0:
            lines.append(
                f"Most positions lost (single stop): {worst_loss[0]} - "
                f"{worst_loss[1].position_change} positions (Lap {worst_loss[1].lap})"
            )

    return "\n".join(lines)
