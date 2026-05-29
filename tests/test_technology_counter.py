"""Tests for technology counter."""

from datetime import date, datetime

from tech_market_analyzer.analysis.technology_counter import TechnologyCounter
from tech_market_analyzer.domain.models import ExperienceLevel, Vacancy, VacancySnapshot


def _make_snapshot(descriptions: list[str]) -> VacancySnapshot:
    vacancies = [
        Vacancy(
            id=str(i),
            title=f"Job {i}",
            company="Co",
            description=desc,
            experience_level=ExperienceLevel.JUNIOR,
            source="test",
            scraped_at=datetime.now(),
        )
        for i, desc in enumerate(descriptions)
    ]
    return VacancySnapshot(
        vacancies=vacancies,
        experience_level=ExperienceLevel.JUNIOR,
        snapshot_date=date.today(),
        source="test",
    )


def test_technology_counter_counts_mentions():
    snapshot = _make_snapshot(
        [
            "Python developer with Django and PostgreSQL",
            "FastAPI and Redis experience required",
            "Django REST framework knowledge",
        ]
    )
    counter = TechnologyCounter()
    stats = counter.analyze(snapshot, ["Django", "PostgreSQL", "FastAPI", "Redis", "Flask"])

    stats_map = {s.technology: s.count for s in stats}
    assert stats_map["Django"] == 2
    assert stats_map["PostgreSQL"] == 1
    assert stats_map["FastAPI"] == 1
    assert "Flask" not in stats_map


def test_technology_counter_empty_snapshot():
    snapshot = _make_snapshot([])
    counter = TechnologyCounter()
    stats = counter.analyze(snapshot, ["Django"])
    assert stats == []
