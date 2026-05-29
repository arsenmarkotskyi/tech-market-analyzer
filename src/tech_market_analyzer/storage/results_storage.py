"""Storage for analysis results (stats JSON and chart images)."""

import json
from datetime import date
from pathlib import Path

from tech_market_analyzer.domain.interfaces import ResultsStorage
from tech_market_analyzer.domain.models import ExperienceLevel, TechnologyStats


class FileResultsStorage(ResultsStorage):
    """Persist analysis results under ``data/results/{date}/``."""

    def __init__(self, results_dir: Path) -> None:
        """Initialize results storage.

        Parameters
        ----------
        results_dir : Path
            Root directory for analysis outputs.
        """
        self.results_dir = results_dir
        self.results_dir.mkdir(parents=True, exist_ok=True)

    def _output_dir(self, snapshot_date: date) -> Path:
        """Return (and create) output directory for a snapshot date."""
        output_dir = self.results_dir / snapshot_date.isoformat()
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir

    def save_stats(
        self,
        stats: list[TechnologyStats],
        snapshot_date: date,
        experience_level: ExperienceLevel,
    ) -> Path:
        """Save technology statistics as JSON."""
        output_dir = self._output_dir(snapshot_date)
        path = output_dir / f"{experience_level.value}_stats.json"
        payload = {
            "snapshot_date": snapshot_date.isoformat(),
            "experience_level": experience_level.value,
            "technologies": [_stats_to_dict(s) for s in stats],
        }
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    def save_chart(
        self,
        stats: list[TechnologyStats],
        snapshot_date: date,
        experience_level: ExperienceLevel,
        top_n: int = 15,
    ) -> Path:
        """Save a bar chart PNG for top technologies."""
        # Lazy import keeps matplotlib optional at import time for storage module
        from tech_market_analyzer.analysis.visualizer import create_bar_chart

        output_dir = self._output_dir(snapshot_date)
        path = output_dir / f"{experience_level.value}_bar_chart.png"
        create_bar_chart(stats, experience_level, path, top_n=top_n)
        return path


def _stats_to_dict(stats: TechnologyStats) -> dict:
    """Serialize TechnologyStats to dict."""
    return {
        "technology": stats.technology,
        "count": stats.count,
        "percentage": stats.percentage,
        "experience_level": stats.experience_level.value,
        "snapshot_date": stats.snapshot_date.isoformat(),
        "total_vacancies": stats.total_vacancies,
    }
