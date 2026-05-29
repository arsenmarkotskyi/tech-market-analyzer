"""Integration tests using real DOU.ua HTML fixtures."""

from pathlib import Path

from tech_market_analyzer.analysis.technology_counter import TechnologyCounter
from tech_market_analyzer.domain.models import ExperienceLevel
from tech_market_analyzer.scraping.parsers import (
    parse_vacancy_detail,
    parse_vacancy_list,
)
from tech_market_analyzer.storage.json_storage import JsonVacancyStorage

FIXTURES_DIR = Path(__file__).parent / "fixtures"

SAMPLE_DETAIL_HTML = """
<html><body>
<div class="b-typo vacancy-section">
  We are looking for a Python developer with Django, PostgreSQL, and Docker experience.
  Knowledge of FastAPI and Redis is a plus. Experience with pytest required.
</div>
</body></html>
"""


def test_parse_real_dou_listing_fixture():
    """Parser extracts vacancies from a real DOU.ua listing HTML snapshot."""
    html = (FIXTURES_DIR / "dou_listing_real.html").read_text(encoding="utf-8")
    results = parse_vacancy_list(html, ExperienceLevel.JUNIOR)

    assert len(results) >= 1
    assert all("id" in item and "title" in item for item in results)
    assert all(item["url"].startswith("http") for item in results)


def test_analyze_junior_snapshot_roundtrip(tmp_path):
    """Load a snapshot fixture, analyze it, and verify technology counts."""
    fixture_path = FIXTURES_DIR / "junior_snapshot.json"

    storage = JsonVacancyStorage(tmp_path)
    snapshot = storage.load_snapshot(fixture_path)

    stats = TechnologyCounter().analyze(
        snapshot, ["Docker", "Git", "PostgreSQL", "Django"]
    )
    stats_map = {s.technology: s.count for s in stats}

    assert stats_map["Docker"] == 1
    assert stats_map["PostgreSQL"] == 2
    assert stats_map["Django"] == 2
    assert snapshot.experience_level == ExperienceLevel.JUNIOR


def test_parse_detail_fixture_extracts_technologies():
    """Detail parser returns description text usable for technology matching."""
    description = parse_vacancy_detail(SAMPLE_DETAIL_HTML)
    assert "Django" in description
    assert "PostgreSQL" in description
