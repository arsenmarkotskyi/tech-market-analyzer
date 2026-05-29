"""Compare technology demand across historical snapshots."""

import json
from datetime import date
from pathlib import Path

from tech_market_analyzer.domain.models import ExperienceLevel, TechnologyStats


def load_stats_file(path: Path) -> list[TechnologyStats]:
    """Load technology stats from a JSON results file.

    Parameters
    ----------
    path : Path
        Path to ``*_stats.json`` file.

    Returns
    -------
    list[TechnologyStats]
        Parsed technology statistics.
    """
    data = json.loads(path.read_text(encoding="utf-8"))
    level = ExperienceLevel.from_string(data["experience_level"])
    snapshot_date = date.fromisoformat(data["snapshot_date"])

    return [
        TechnologyStats(
            technology=item["technology"],
            count=item["count"],
            percentage=item["percentage"],
            experience_level=level,
            snapshot_date=snapshot_date,
            total_vacancies=item["total_vacancies"],
        )
        for item in data["technologies"]
    ]


def compare_snapshots(
    older_stats: list[TechnologyStats],
    newer_stats: list[TechnologyStats],
    top_n: int = 10,
) -> list[dict]:
    """Compare two snapshots and compute trend per technology.

    Parameters
    ----------
    older_stats : list[TechnologyStats]
        Statistics from the older snapshot.
    newer_stats : list[TechnologyStats]
        Statistics from the newer snapshot.
    top_n : int
        Number of top technologies from newer snapshot to include.

    Returns
    -------
    list[dict]
        Comparison rows with keys: technology, old_count, new_count, change, trend.
    """
    older_map = {s.technology: s.count for s in older_stats}
    newer_map = {s.technology: s.count for s in newer_stats}

    top_techs = [s.technology for s in newer_stats[:top_n]]
    all_techs = set(older_map) | set(newer_map)
    focus = top_techs or sorted(all_techs)

    results = []
    for tech in focus:
        old_count = older_map.get(tech, 0)
        new_count = newer_map.get(tech, 0)
        change = new_count - old_count
        if change > 0:
            trend = "up"
        elif change < 0:
            trend = "down"
        else:
            trend = "stable"

        results.append(
            {
                "technology": tech,
                "old_count": old_count,
                "new_count": new_count,
                "change": change,
                "trend": trend,
            }
        )

    return sorted(results, key=lambda r: r["new_count"], reverse=True)
