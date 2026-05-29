"""HTML parsers for job vacancy pages."""

import logging
import re
from datetime import datetime

from bs4 import BeautifulSoup

from tech_market_analyzer.domain.models import ExperienceLevel, Vacancy

logger = logging.getLogger(__name__)


def parse_vacancy_list(html: str, experience_level: ExperienceLevel) -> list[dict]:
    """Parse vacancy listing page and extract basic vacancy data.

    This is a skeleton parser for DOU.ua. Update CSS selectors after
    inspecting the live HTML structure with browser DevTools.

    Parameters
    ----------
    html : str
        Raw HTML of the vacancies listing page.
    experience_level : ExperienceLevel
        Experience level filter applied during scraping.

    Returns
    -------
    list[dict]
        List of dicts with keys: id, title, company, url, description, salary, location.
    """
    soup = BeautifulSoup(html, "lxml")
    vacancies: list[dict] = []

    for item in soup.select("li.l-vacancy"):
        title_el = item.select_one("a.vt")
        company_el = item.select_one("a.company")
        if not title_el:
            continue

        url = title_el.get("href", "")
        vacancy_id = _extract_id_from_url(url)
        salary_el = item.select_one("span.salary")
        location_el = item.select_one("span.cities")

        vacancies.append(
            {
                "id": vacancy_id,
                "title": title_el.get_text(strip=True),
                "company": company_el.get_text(strip=True) if company_el else "Unknown",
                "url": url if url.startswith("http") else f"https://jobs.dou.ua{url}",
                "description": "",
                "salary": salary_el.get_text(strip=True) if salary_el else None,
                "location": location_el.get_text(strip=True) if location_el else None,
            }
        )

    if not vacancies:
        logger.warning(
            "No vacancies parsed — CSS selectors may be outdated. "
            "Inspect jobs.dou.ua HTML and update parsers.py"
        )

    return vacancies


def parse_vacancy_detail(html: str) -> str:
    """Parse full vacancy description from a detail page."""
    return parse_vacancy_detail_page(html)["description"]


def parse_engagement_stats(html: str) -> dict[str, int | None]:
    """Extract public applications count when present on the detail page."""
    soup = BeautifulSoup(html, "lxml")
    text = soup.get_text(" ", strip=True)

    applications = _find_count(
        text,
        [
            r"(\d+)\s*відгук",  # Ukrainian: applications/replies
            r"(\d+)\s*applications?",
            r"(\d+)\s*replies",
        ],
    )
    return {"applications": applications}


def parse_vacancy_detail_page(html: str) -> dict[str, str | int | None]:
    """Parse description and optional applications count from a detail page."""
    soup = BeautifulSoup(html, "lxml")
    description_el = soup.select_one("div.b-typo.vacancy-section")
    description = (
        description_el.get_text(separator=" ", strip=True) if description_el else ""
    )
    engagement = parse_engagement_stats(html)
    return {
        "description": description,
        "applications": engagement["applications"],
    }


def _find_count(text: str, patterns: list[str]) -> int | None:
    """Return first integer match from regex patterns."""
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return int(match.group(1))
    return None


def build_vacancy(
    raw: dict,
    experience_level: ExperienceLevel,
    source: str = "dou.ua",
) -> Vacancy:
    """Build a Vacancy domain object from parsed raw data.

    Parameters
    ----------
    raw : dict
        Parsed vacancy fields.
    experience_level : ExperienceLevel
        Experience level for this vacancy.
    source : str
        Source site identifier.

    Returns
    -------
    Vacancy
        Populated Vacancy instance.
    """
    return Vacancy(
        id=raw["id"],
        title=raw["title"],
        company=raw["company"],
        description=raw.get("description", ""),
        experience_level=experience_level,
        source=source,
        scraped_at=datetime.now(),
        salary=raw.get("salary"),
        location=raw.get("location"),
        applications=raw.get("applications"),
        url=raw.get("url"),
    )


def _extract_id_from_url(url: str) -> str:
    """Extract numeric vacancy ID from URL path."""
    match = re.search(r"/vacancies/(\d+)", url)
    return match.group(1) if match else url.strip("/").split("/")[-1]
