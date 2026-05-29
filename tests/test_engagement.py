"""Tests for engagement analysis."""

from datetime import date, datetime

from tech_market_analyzer.analysis.engagement import analyze_engagement
from tech_market_analyzer.domain.models import ExperienceLevel, Vacancy, VacancySnapshot


def _vacancy(vid: str, apps, desc: str, location: str | None = None) -> Vacancy:
    return Vacancy(
        id=vid,
        title=f"Job {vid}",
        company="Co",
        description=desc,
        experience_level=ExperienceLevel.MIDDLE,
        source="test",
        scraped_at=datetime.now(),
        location=location,
        applications=apps,
    )


def test_engagement_correlations_with_synthetic_data():
    snapshot = VacancySnapshot(
        vacancies=[
            _vacancy("1", 5, "Python Django PostgreSQL Redis Docker", "віддалено"),
            _vacancy("2", 10, "Python", "Київ"),
            _vacancy("3", 2, "Python FastAPI Docker Kubernetes AWS"),
            _vacancy("4", 8, "Python Django Flask", "Львів"),
        ],
        experience_level=ExperienceLevel.MIDDLE,
        snapshot_date=date.today(),
        source="test",
    )

    report = analyze_engagement(snapshot)
    assert report.with_applications == 4
    assert report.correlations["applications_vs_tech_count"] is not None
    assert report.top_low_competition[0]["applications"] == 2


def test_engagement_handles_missing_metrics():
    snapshot = VacancySnapshot(
        vacancies=[_vacancy("1", None, "Python only")],
        experience_level=ExperienceLevel.JUNIOR,
        snapshot_date=date.today(),
        source="test",
    )
    report = analyze_engagement(snapshot)
    assert report.with_applications == 0
    assert report.correlations["applications_vs_tech_count"] is None
