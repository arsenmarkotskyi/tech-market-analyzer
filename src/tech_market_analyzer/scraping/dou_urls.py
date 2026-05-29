"""Shared DOU.ua URL builders and experience filter slugs."""

from urllib.parse import quote_plus

from tech_market_analyzer.domain.models import ExperienceLevel

# DOU.ua experience ranges (?exp=...) — see jobs.dou.ua vacancy filters
EXPERIENCE_SLUGS: dict[ExperienceLevel, list[str]] = {
    ExperienceLevel.JUNIOR: ["0-1"],
    ExperienceLevel.MIDDLE: ["1-3"],
    ExperienceLevel.SENIOR: ["3-5", "5plus"],
}


def build_search_url(
    base_url: str,
    category: str,
    exp_slug: str,
    page: int = 0,
) -> str:
    """Build a DOU.ua vacancy search URL for category, experience, and page."""
    category_param = quote_plus(category)
    offset = page * 20
    return (
        f"{base_url.rstrip('/')}/vacancies/?"
        f"category={category_param}&exp={exp_slug}&offset={offset}"
    )
