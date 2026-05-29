"""Tests for DOU URL builders."""

from tech_market_analyzer.domain.models import ExperienceLevel
from tech_market_analyzer.scraping.dou_urls import EXPERIENCE_SLUGS, build_search_url


def test_experience_slugs_use_dou_ranges():
    assert EXPERIENCE_SLUGS[ExperienceLevel.JUNIOR] == ["0-1"]
    assert EXPERIENCE_SLUGS[ExperienceLevel.MIDDLE] == ["1-3"]
    assert EXPERIENCE_SLUGS[ExperienceLevel.SENIOR] == ["3-5", "5plus"]


def test_build_search_url_uses_category_and_exp_range():
    url = build_search_url("https://jobs.dou.ua", "Python", "1-3", page=0)
    assert "category=Python" in url
    assert "exp=1-3" in url
    assert "offset=0" in url

    url_page_2 = build_search_url("https://jobs.dou.ua", "Python", "0-1", page=2)
    assert "exp=0-1" in url_page_2
    assert "offset=40" in url_page_2
