"""Abstract interfaces (protocols) for scraping, storage, and analysis."""

from abc import ABC, abstractmethod
from datetime import date
from pathlib import Path

from tech_market_analyzer.domain.models import (
    ExperienceLevel,
    TechnologyStats,
    Vacancy,
    VacancySnapshot,
)


class Scraper(ABC):
    """Abstract base class for job vacancy scrapers."""

    @abstractmethod
    def scrape(self, experience_level: ExperienceLevel) -> VacancySnapshot:
        """Scrape vacancies for a given experience level.

        Parameters
        ----------
        experience_level : ExperienceLevel
            Target experience level filter.

        Returns
        -------
        VacancySnapshot
            Collected vacancies with metadata.
        """

    @abstractmethod
    def scrape_all_levels(self) -> list[VacancySnapshot]:
        """Scrape vacancies for all configured experience levels.

        Returns
        -------
        list[VacancySnapshot]
            One snapshot per experience level.
        """


class VacancyStorage(ABC):
    """Abstract base class for vacancy persistence."""

    @abstractmethod
    def save_snapshot(self, snapshot: VacancySnapshot) -> Path:
        """Persist a vacancy snapshot to storage.

        Parameters
        ----------
        snapshot : VacancySnapshot
            Snapshot to save.

        Returns
        -------
        Path
            Path to the saved file.
        """

    @abstractmethod
    def load_snapshot(self, path: Path) -> VacancySnapshot:
        """Load a vacancy snapshot from storage.

        Parameters
        ----------
        path : Path
            Path to the snapshot file.

        Returns
        -------
        VacancySnapshot
            Loaded snapshot.
        """

    @abstractmethod
    def list_snapshots(
        self, experience_level: ExperienceLevel | None = None
    ) -> list[Path]:
        """List available snapshot files, optionally filtered by level.

        Parameters
        ----------
        experience_level : ExperienceLevel | None
            If set, return only snapshots for this level.

        Returns
        -------
        list[Path]
            Sorted list of snapshot file paths (newest first).
        """

    @abstractmethod
    def get_latest_snapshot(
        self, experience_level: ExperienceLevel
    ) -> Path | None:
        """Return path to the most recent snapshot for a level.

        Parameters
        ----------
        experience_level : ExperienceLevel
            Target experience level.

        Returns
        -------
        Path | None
            Latest snapshot path, or None if not found.
        """


class TechnologyAnalyzer(ABC):
    """Abstract base class for technology demand analysis."""

    @abstractmethod
    def analyze(
        self,
        snapshot: VacancySnapshot,
        technologies: list[str],
    ) -> list[TechnologyStats]:
        """Count technology mentions across vacancies in a snapshot.

        Parameters
        ----------
        snapshot : VacancySnapshot
            Vacancy data to analyze.
        technologies : list[str]
            Technology keywords to search for.

        Returns
        -------
        list[TechnologyStats]
            Stats sorted by count descending.
        """


class ResultsStorage(ABC):
    """Abstract base class for analysis results persistence."""

    @abstractmethod
    def save_stats(
        self,
        stats: list[TechnologyStats],
        snapshot_date: date,
        experience_level: ExperienceLevel,
    ) -> Path:
        """Save technology statistics as JSON.

        Parameters
        ----------
        stats : list[TechnologyStats]
            Statistics to persist.
        snapshot_date : date
            Date of the source snapshot.
        experience_level : ExperienceLevel
            Experience level analyzed.

        Returns
        -------
        Path
            Path to saved stats file.
        """

    @abstractmethod
    def save_chart(
        self,
        stats: list[TechnologyStats],
        snapshot_date: date,
        experience_level: ExperienceLevel,
        top_n: int = 15,
    ) -> Path:
        """Save a bar chart visualization.

        Parameters
        ----------
        stats : list[TechnologyStats]
            Statistics to visualize.
        snapshot_date : date
            Date of the source snapshot.
        experience_level : ExperienceLevel
            Experience level analyzed.
        top_n : int
            Number of top technologies to show.

        Returns
        -------
        Path
            Path to saved chart image.
        """
