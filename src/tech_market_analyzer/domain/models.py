"""Domain models for vacancies and technology statistics."""

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum


class ExperienceLevel(str, Enum):
    """Experience level filter for job vacancies."""

    JUNIOR = "junior"
    MIDDLE = "middle"
    SENIOR = "senior"

    @classmethod
    def from_string(cls, value: str) -> "ExperienceLevel":
        """Parse experience level from string value.

        Parameters
        ----------
        value : str
            Raw level string (case-insensitive).

        Returns
        -------
        ExperienceLevel
            Matching enum member.

        Raises
        ------
        ValueError
            If value does not match any known level.
        """
        normalized = value.strip().lower()
        for member in cls:
            if member.value == normalized:
                return member
        raise ValueError(f"Unknown experience level: {value!r}")


@dataclass
class Vacancy:
    """A single job vacancy scraped from a public job board.

    Attributes
    ----------
    id : str
        Unique vacancy identifier from the source site.
    title : str
        Job title.
    company : str
        Company name.
    description : str
        Full vacancy description text.
    experience_level : ExperienceLevel
        Target experience level (junior/middle/senior).
    source : str
        Source website identifier (e.g. ``dou.ua``).
    scraped_at : datetime
        Timestamp when the vacancy was scraped.
    salary : str | None
        Salary text if available.
    location : str | None
        City or work format (e.g. ``remote``, ``Kyiv``) from listing page.
    applications : int | None
        Number of applications if publicly available.
    url : str | None
        Direct link to the vacancy page.
    """

    id: str
    title: str
    company: str
    description: str
    experience_level: ExperienceLevel
    source: str
    scraped_at: datetime
    salary: str | None = None
    location: str | None = None
    applications: int | None = None
    url: str | None = None


@dataclass
class TechnologyStats:
    """Aggregated statistics for a single technology.

    Attributes
    ----------
    technology : str
        Technology name.
    count : int
        Number of vacancies mentioning this technology.
    percentage : float
        Share of total vacancies (0-100).
    experience_level : ExperienceLevel
        Experience level this stat belongs to.
    snapshot_date : date
        Date of the data snapshot.
    total_vacancies : int
        Total vacancies analyzed for this snapshot.
    """

    technology: str
    count: int
    percentage: float
    experience_level: ExperienceLevel
    snapshot_date: date
    total_vacancies: int


@dataclass
class VacancySnapshot:
    """A batch of vacancies saved at a specific point in time.

    Attributes
    ----------
    vacancies : list[Vacancy]
        Collected vacancies.
    experience_level : ExperienceLevel
        Experience level filter used during scraping.
    snapshot_date : date
        Date of the snapshot.
    source : str
        Data source identifier.
    """

    vacancies: list[Vacancy] = field(default_factory=list)
    experience_level: ExperienceLevel = ExperienceLevel.JUNIOR
    snapshot_date: date = field(default_factory=date.today)
    source: str = "dou.ua"

    @property
    def total(self) -> int:
        """Return total number of vacancies in this snapshot."""
        return len(self.vacancies)
