"""CLI entry point for the analysis module (runs independently)."""

import logging
from pathlib import Path

from tech_market_analyzer.analysis.history import compare_snapshots, load_stats_file
from tech_market_analyzer.analysis.technology_counter import TechnologyCounter
from tech_market_analyzer.domain.models import ExperienceLevel
from tech_market_analyzer.settings import get_settings, load_technologies
from tech_market_analyzer.storage.json_storage import JsonVacancyStorage
from tech_market_analyzer.storage.results_storage import FileResultsStorage

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def run_analysis(
    input_path: Path | None = None,
    latest: bool = False,
    level: ExperienceLevel = ExperienceLevel.JUNIOR,
    top_n: int = 15,
) -> tuple[Path, Path]:
    """Run technology analysis on a vacancy snapshot.

    Parameters
    ----------
    input_path : Path | None
        Explicit path to a raw snapshot JSON file.
    latest : bool
        If True, use the latest snapshot for the given level.
    level : ExperienceLevel
        Experience level when using ``--latest``.
    top_n : int
        Number of top technologies for the chart.

    Returns
    -------
    tuple[Path, Path]
        Paths to saved stats JSON and chart PNG.
    """
    settings = get_settings()
    vacancy_storage = JsonVacancyStorage(settings.raw_data_dir)
    results_storage = FileResultsStorage(settings.results_dir)
    technologies = load_technologies(settings.technologies_config)

    if input_path:
        snapshot_path = input_path
    elif latest:
        snapshot_path = vacancy_storage.get_latest_snapshot(level)
        if snapshot_path is None:
            raise FileNotFoundError(f"No snapshots found for level={level.value}")
    else:
        raise ValueError("Provide --input or --latest")

    logger.info("Loading snapshot: %s", snapshot_path)
    snapshot = vacancy_storage.load_snapshot(snapshot_path)

    counter = TechnologyCounter()
    stats = counter.analyze(snapshot, technologies)

    stats_path = results_storage.save_stats(
        stats, snapshot.snapshot_date, snapshot.experience_level
    )
    chart_path = results_storage.save_chart(
        stats, snapshot.snapshot_date, snapshot.experience_level, top_n=top_n
    )

    logger.info("Saved stats: %s", stats_path)
    logger.info("Saved chart: %s", chart_path)

    _print_top_stats(stats, top_n=10)
    return stats_path, chart_path


def run_history_comparison(
    older_date: str,
    newer_date: str,
    level: ExperienceLevel = ExperienceLevel.JUNIOR,
) -> None:
    """Compare technology stats between two snapshot dates.

    Parameters
    ----------
    older_date : str
        Older snapshot date (ISO format).
    newer_date : str
        Newer snapshot date (ISO format).
    level : ExperienceLevel
        Experience level to compare.
    """
    settings = get_settings()
    older_path = settings.results_dir / older_date / f"{level.value}_stats.json"
    newer_path = settings.results_dir / newer_date / f"{level.value}_stats.json"

    older_stats = load_stats_file(older_path)
    newer_stats = load_stats_file(newer_path)
    comparison = compare_snapshots(older_stats, newer_stats)

    print(f"\nTrend comparison ({level.value}): {older_date} → {newer_date}")
    print("-" * 50)
    for row in comparison:
        arrow = {"up": "↑", "down": "↓", "stable": "→"}[row["trend"]]
        print(
            f"  {row['technology']:20s}  "
            f"{row['old_count']:3d} → {row['new_count']:3d}  "
            f"({row['change']:+d}) {arrow}"
        )


def _print_top_stats(stats: list, top_n: int = 10) -> None:
    """Print top technologies to console."""
    print(f"\nTop {top_n} technologies:")
    for i, stat in enumerate(stats[:top_n], 1):
        print(f"  {i:2d}. {stat.technology:20s}  {stat.count:3d}  ({stat.percentage}%)")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Analyze technology demand")
    parser.add_argument("--input", type=Path, help="Path to raw snapshot JSON")
    parser.add_argument("--latest", action="store_true", help="Use latest snapshot")
    parser.add_argument(
        "--level",
        choices=["junior", "middle", "senior"],
        default="junior",
        help="Experience level for --latest",
    )
    parser.add_argument("--top-n", type=int, default=15, help="Top N for chart")
    parser.add_argument("--compare", nargs=2, metavar=("OLDER", "NEWER"))
    args = parser.parse_args()

    if args.compare:
        run_history_comparison(
            args.compare[0], args.compare[1], ExperienceLevel.from_string(args.level)
        )
    else:
        run_analysis(
            input_path=args.input,
            latest=args.latest,
            level=ExperienceLevel.from_string(args.level),
            top_n=args.top_n,
        )
