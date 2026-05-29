"""Tests for JSON vacancy storage."""

import json
from datetime import date, datetime
from pathlib import Path

from tech_market_analyzer.domain.models import ExperienceLevel, Vacancy, VacancySnapshot
from tech_market_analyzer.storage.json_storage import JsonVacancyStorage


def test_save_and_load_snapshot(tmp_path: Path):
    vacancy = Vacancy(
        id="1",
        title="Python Dev",
        company="ACME",
        description="Django, Docker",
        experience_level=ExperienceLevel.SENIOR,
        source="dou.ua",
        scraped_at=datetime(2026, 5, 29, 12, 0, 0),
        url="https://jobs.dou.ua/vacancies/1/",
    )
    snapshot = VacancySnapshot(
        vacancies=[vacancy],
        experience_level=ExperienceLevel.SENIOR,
        snapshot_date=date(2026, 5, 29),
        source="dou.ua",
    )

    storage = JsonVacancyStorage(tmp_path)
    saved_path = storage.save_snapshot(snapshot)
    assert saved_path.exists()

    loaded = storage.load_snapshot(saved_path)
    assert loaded.total == 1
    assert loaded.vacancies[0].title == "Python Dev"
    assert loaded.experience_level == ExperienceLevel.SENIOR


def test_list_snapshots_sorted_newest_first(tmp_path: Path):
    storage = JsonVacancyStorage(tmp_path)

    for day in [27, 28, 29]:
        snapshot = VacancySnapshot(
            vacancies=[],
            experience_level=ExperienceLevel.JUNIOR,
            snapshot_date=date(2026, 5, day),
        )
        storage.save_snapshot(snapshot)

    files = storage.list_snapshots(ExperienceLevel.JUNIOR)
    assert len(files) == 3
    assert "2026-05-29" in files[0].name
