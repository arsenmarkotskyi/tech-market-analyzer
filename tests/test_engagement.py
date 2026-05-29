"""Tests for engagement analysis."""

from datetime import date, datetime

from tech_market_analyzer.analysis.engagement import analyze_engagement
from tech_market_analyzer.domain.models import ExperienceLevel, Vacancy, VacancySnapshot


def _vacancy(vid: str, views, apps, desc: str) -> Vacancy:
    return Vacancy(
        id=vid,
        title=f"Job {vid}",
        company="Co",
        description=desc,
        experience_level=ExperienceLevel.MIDDLE,
        source="test",
        scraped_at=datetime.now(),
        views=views,
        applications=apps,
    )


def test_engagement_correlations_with_synthetic_data():
    snapshot = VacancySnapshot(
        vacancies=[
            _vacancy("1", 100, 5, "Python Django PostgreSQL Redis Docker"),
            _vacancy("2", 200, 10, "Python"),
            _vacancy("3", 150, 2, "Python FastAPI Docker Kubernetes AWS"),
            _vacancy("4", 80, 8, "Python Django Flask"),
        ],
        experience_level=ExperienceLevel.MIDDLE,
        snapshot_date=date.today(),
        source="test",
    )

    report = analyze_engagement(snapshot)
    assert report.with_views == 4
    assert report.with_applications == 4
    assert report.correlations["views_vs_tech_count"] is not None


def test_engagement_handles_missing_metrics():
    snapshot = VacancySnapshot(
        vacancies=[_vacancy("1", None, None, "Python only")],
        experience_level=ExperienceLevel.JUNIOR,
        snapshot_date=date.today(),
        source="test",
    )
    report = analyze_engagement(snapshot)
    assert report.with_views == 0
    assert report.correlations["views_vs_tech_count"] is None
