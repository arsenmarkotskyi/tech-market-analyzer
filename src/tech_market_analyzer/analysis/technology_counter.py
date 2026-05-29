"""Count technology mentions in vacancy descriptions."""

import re

from tech_market_analyzer.domain.interfaces import TechnologyAnalyzer
from tech_market_analyzer.domain.models import TechnologyStats, VacancySnapshot


class TechnologyCounter(TechnologyAnalyzer):
    """Count configured technology keywords in vacancy descriptions.

    Uses case-insensitive matching with word boundaries to reduce
    false positives (e.g. ``go`` inside ``django``).
    """

    def analyze(
        self,
        snapshot: VacancySnapshot,
        technologies: list[str],
    ) -> list[TechnologyStats]:
        """Count technology mentions across all vacancies in snapshot.

        Parameters
        ----------
        snapshot : VacancySnapshot
            Vacancy data to analyze.
        technologies : list[str]
            Technology keywords from config.

        Returns
        -------
        list[TechnologyStats]
            Stats sorted by count descending.
        """
        total = snapshot.total
        if total == 0:
            return []

        counts: dict[str, int] = {tech: 0 for tech in technologies}

        for vacancy in snapshot.vacancies:
            text = vacancy.description.lower()
            for tech in technologies:
                if _matches_technology(text, tech):
                    counts[tech] += 1

        stats = [
            TechnologyStats(
                technology=tech,
                count=count,
                percentage=round(count / total * 100, 2),
                experience_level=snapshot.experience_level,
                snapshot_date=snapshot.snapshot_date,
                total_vacancies=total,
            )
            for tech, count in counts.items()
            if count > 0
        ]

        return sorted(stats, key=lambda s: s.count, reverse=True)


def _matches_technology(text: str, technology: str) -> bool:
    """Check if technology appears in text with word boundaries.

    Parameters
    ----------
    text : str
        Lowercased description text.
    technology : str
        Technology keyword (original casing preserved for regex).

    Returns
    -------
    bool
        True if technology is found.
    """
    # Escape special regex chars but keep word boundary logic
    escaped = re.escape(technology.lower())
    pattern = rf"\b{escaped}\b"
    return bool(re.search(pattern, text, re.IGNORECASE))
