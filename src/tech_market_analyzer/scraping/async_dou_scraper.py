"""Async DOU.ua scraper using aiohttp for parallel detail fetching."""

import asyncio
import logging
from datetime import date

import aiohttp

from tech_market_analyzer.domain.models import ExperienceLevel, Vacancy, VacancySnapshot
from tech_market_analyzer.scraping.async_base import AsyncBaseScraper
from tech_market_analyzer.scraping.dou_urls import EXPERIENCE_SLUGS, build_search_url
from tech_market_analyzer.scraping.parsers import (
    build_vacancy,
    parse_vacancy_detail_page,
    parse_vacancy_list,
)
from tech_market_analyzer.settings import Settings, get_settings

logger = logging.getLogger(__name__)


class AsyncDouScraper(AsyncBaseScraper):
    """Async variant of DouScraper with concurrent detail page fetching."""

    def __init__(self, settings: Settings | None = None) -> None:
        """Initialize async DOU scraper."""
        self.settings = settings or get_settings()
        super().__init__(
            user_agent=self.settings.user_agent,
            request_delay_seconds=self.settings.request_delay_seconds,
            max_concurrency=self.settings.async_max_concurrency,
        )
        self.base_url = self.settings.base_url.rstrip("/")
        self.max_pages = self.settings.max_pages
        self.category = self.settings.category

    def _build_detail_url(self, vacancy_url: str) -> str:
        """Ensure vacancy detail URL is absolute."""
        if vacancy_url.startswith("http"):
            return vacancy_url
        return f"{self.base_url}{vacancy_url}"

    async def _enrich_vacancy(
        self,
        session: aiohttp.ClientSession,
        raw: dict,
        experience_level: ExperienceLevel,
    ) -> Vacancy:
        """Fetch detail page and build a Vacancy."""
        detail_url = self._build_detail_url(raw["url"])
        detail_html = await self.fetch_page(session, detail_url)
        detail = parse_vacancy_detail_page(detail_html)
        raw["description"] = detail["description"]
        raw["views"] = detail.get("views")
        raw["applications"] = detail.get("applications")
        return build_vacancy(raw, experience_level, source="dou.ua")

    async def scrape(self, experience_level: ExperienceLevel) -> VacancySnapshot:
        """Scrape vacancies for one experience level asynchronously."""
        all_vacancies: list[Vacancy] = []
        seen_ids: set[str] = set()
        timeout = aiohttp.ClientTimeout(total=60)

        async with aiohttp.ClientSession(timeout=timeout) as session:
            for exp_slug in EXPERIENCE_SLUGS[experience_level]:
                logger.info(
                    "Async scraping level=%s with exp=%s",
                    experience_level.value,
                    exp_slug,
                )
                for page in range(self.max_pages):
                    url = build_search_url(self.base_url, self.category, exp_slug, page)
                    logger.info("Fetching page %d: %s", page + 1, url)

                    html = await self.fetch_page(session, url)
                    raw_list = parse_vacancy_list(html, experience_level)
                    if not raw_list:
                        break

                    new_items = [r for r in raw_list if r["id"] not in seen_ids]
                    for raw in new_items:
                        seen_ids.add(raw["id"])

                    if not new_items:
                        break

                    tasks = [
                        self._enrich_vacancy(session, raw, experience_level)
                        for raw in new_items
                    ]
                    vacancies = await asyncio.gather(*tasks)
                    all_vacancies.extend(vacancies)

        logger.info(
            "Async scraped %d vacancies for level=%s",
            len(all_vacancies),
            experience_level.value,
        )
        return VacancySnapshot(
            vacancies=all_vacancies,
            experience_level=experience_level,
            snapshot_date=date.today(),
            source="dou.ua",
        )

    async def scrape_all_levels(self) -> list[VacancySnapshot]:
        """Scrape all experience levels."""
        return [await self.scrape(level) for level in ExperienceLevel]
