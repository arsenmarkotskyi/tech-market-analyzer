"""DOU.ua job vacancy scraper implementation."""

import logging
from datetime import date
from urllib.parse import quote_plus

from tech_market_analyzer.domain.interfaces import Scraper
from tech_market_analyzer.domain.models import (
    ExperienceLevel,
    Vacancy,
    VacancySnapshot,
)
from tech_market_analyzer.scraping.base import BaseScraper
from tech_market_analyzer.scraping.parsers import (
    build_vacancy,
    parse_vacancy_detail,
    parse_vacancy_list,
)
from tech_market_analyzer.settings import Settings, get_settings

logger = logging.getLogger(__name__)

# DOU.ua experience filter values (?exp=...) on jobs.dou.ua
EXPERIENCE_SLUGS: dict[ExperienceLevel, str] = {
    ExperienceLevel.JUNIOR: "0",       # без досвіду
    ExperienceLevel.MIDDLE: "1",        # від 1 року
    ExperienceLevel.SENIOR: "5plus",    # від 5 років (exp=3 often empty for Python)
}


class DouScraper(BaseScraper, Scraper):
    """Scrape Python vacancies from jobs.dou.ua."""

    def __init__(self, settings: Settings | None = None) -> None:
        """Initialize DOU scraper with application settings."""
        self.settings = settings or get_settings()
        super().__init__(
            base_url=self.settings.base_url,
            user_agent=self.settings.user_agent,
            request_delay_seconds=self.settings.request_delay_seconds,
            max_pages=self.settings.max_pages,
        )
    def _build_search_url(self, experience_level: ExperienceLevel, page: int = 0) -> str:
        """Build search URL for a given experience level and page."""
        slug = EXPERIENCE_SLUGS[experience_level]
        category = quote_plus(self.settings.category)
        offset = page * 20  # DOU typically shows 20 per page
        return (
            f"{self.base_url}/vacancies/?"
            f"category={category}&exp={slug}&offset={offset}"
        )

    def _build_detail_url(self, vacancy_url: str) -> str:
        """Ensure vacancy detail URL is absolute."""
        if vacancy_url.startswith("http"):
            return vacancy_url
        return f"{self.base_url}{vacancy_url}"

    def scrape(self, experience_level: ExperienceLevel) -> VacancySnapshot:
        """Scrape all pages of Python vacancies for one experience level."""
        all_vacancies: list[Vacancy] = []
        seen_ids: set[str] = set()

        for page in range(self.max_pages):
            url = self._build_search_url(experience_level, page)
            logger.info("Fetching page %d: %s", page + 1, url)

            html = self.fetch_page(url)
            raw_list = parse_vacancy_list(html, experience_level)

            if not raw_list:
                logger.info("No more vacancies on page %d, stopping.", page + 1)
                break

            new_on_page = 0
            for raw in raw_list:
                if raw["id"] in seen_ids:
                    continue
                seen_ids.add(raw["id"])

                # Fetch detail page only for new vacancies (minimize requests)
                detail_url = self._build_detail_url(raw["url"])
                detail_html = self.fetch_page(detail_url)
                raw["description"] = parse_vacancy_detail(detail_html)

                all_vacancies.append(
                    build_vacancy(raw, experience_level, source="dou.ua")
                )
                new_on_page += 1

            if new_on_page == 0:
                break

        logger.info(
            "Scraped %d vacancies for level=%s",
            len(all_vacancies),
            experience_level.value,
        )

        return VacancySnapshot(
            vacancies=all_vacancies,
            experience_level=experience_level,
            snapshot_date=date.today(),
            source="dou.ua",
        )

    def scrape_all_levels(self) -> list[VacancySnapshot]:
        """Scrape vacancies for junior, middle, and senior levels."""
        return [self.scrape(level) for level in ExperienceLevel]
