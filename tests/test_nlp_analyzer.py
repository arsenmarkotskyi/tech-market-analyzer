"""Tests for NLP word frequency analyzer."""

from datetime import date, datetime

import pytest

from tech_market_analyzer.analysis.nlp_analyzer import analyze_word_frequency
from tech_market_analyzer.domain.models import ExperienceLevel, Vacancy, VacancySnapshot

pytest.importorskip("nltk")


def _snapshot(descriptions: list[str]) -> VacancySnapshot:
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


def test_nlp_analyzer_finds_technology_words():
    snapshot = _snapshot(
        [
            "Python Django PostgreSQL Docker deployment",
            "FastAPI Redis Kubernetes CI/CD pipeline",
        ]
    )
    stats = analyze_word_frequency(snapshot, top_n=10)
    words = {s.word for s in stats}
    assert "django" in words
    assert "postgresql" in words
    assert "the" not in words
