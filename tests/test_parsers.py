"""Tests for HTML parsers."""

from tech_market_analyzer.domain.models import ExperienceLevel
from tech_market_analyzer.scraping.parsers import (
    build_vacancy,
    parse_vacancy_detail,
    parse_vacancy_list,
)

SAMPLE_LISTING_HTML = """
<html><body>
<ul>
  <li class="l-vacancy">
    <a class="vt" href="/vacancies/123456/">Python Developer</a>
    <a class="company">Test Company</a>
  </li>
</ul>
</body></html>
"""

SAMPLE_DETAIL_HTML = """
<html><body>
<div class="b-typo vacancy-section">
  Python developer with Django and PostgreSQL experience.
</div>
</body></html>
"""


def test_parse_vacancy_list_extracts_basic_fields():
    results = parse_vacancy_list(SAMPLE_LISTING_HTML, ExperienceLevel.JUNIOR)
    assert len(results) == 1
    assert results[0]["title"] == "Python Developer"
    assert results[0]["company"] == "Test Company"
    assert results[0]["id"] == "123456"
    assert results[0]["salary"] is None


def test_parse_vacancy_list_extracts_salary():
    html = """
    <html><body>
    <li class="l-vacancy">
      <div class="title">
        <a class="vt" href="https://jobs.dou.ua/companies/orange-uni/vacancies/348148/">
          Senior Backend Developer (Python, Django) — Remote
        </a>
        <strong>в <a class="company" href="...">Orange Uni</a></strong>
        <span class="salary">$2000–3200</span>
        <span class="cities bi bi-geo-alt-fill"> віддалено</span>
      </div>
    </li>
    </body></html>
    """
    results = parse_vacancy_list(html, ExperienceLevel.SENIOR)
    assert len(results) == 1
    assert results[0]["salary"] == "$2000–3200"
    assert results[0]["company"] == "Orange Uni"


def test_parse_vacancy_list_extracts_location():
    html = """
    <html><body>
    <li class="l-vacancy">
      <div class="title">
        <a class="vt"
           href="https://jobs.dou.ua/companies/come-back-agency/vacancies/359598/">
          Junior Python Developer
        </a>
        <strong>в <a class="company">Come Back Agency</a></strong>
        <span class="cities bi bi-geo-alt-fill"> віддалено</span>
      </div>
    </li>
    </body></html>
    """
    results = parse_vacancy_list(html, ExperienceLevel.JUNIOR)
    assert results[0]["location"] == "віддалено"


def test_parse_vacancy_detail_extracts_description():
    description = parse_vacancy_detail(SAMPLE_DETAIL_HTML)
    assert "Django" in description
    assert "PostgreSQL" in description


def test_build_vacancy_creates_domain_object():
    raw = {
        "id": "123",
        "title": "Python Dev",
        "company": "ACME",
        "description": "Django, Flask",
        "url": "https://jobs.dou.ua/vacancies/123/",
    }
    vacancy = build_vacancy(raw, ExperienceLevel.MIDDLE)
    assert vacancy.id == "123"
    assert vacancy.experience_level == ExperienceLevel.MIDDLE
    assert vacancy.source == "dou.ua"
