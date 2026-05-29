"""CLI entry point for the scraping module (runs independently)."""

import asyncio
import logging
from pathlib import Path

from tech_market_analyzer.domain.models import ExperienceLevel
from tech_market_analyzer.scraping.async_dou_scraper import AsyncDouScraper
from tech_market_analyzer.scraping.dou_scraper import DouScraper
from tech_market_analyzer.settings import get_settings
from tech_market_analyzer.storage.json_storage import JsonVacancyStorage

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def run_scraping(
    level: ExperienceLevel | None = None,
    all_levels: bool = False,
    force: bool = False,
    use_async: bool = False,
) -> list[Path]:
    """Run scraping and save snapshots to disk."""
    if use_async:
        return asyncio.run(
            _run_scraping_async(level=level, all_levels=all_levels, force=force)
        )
    return _run_scraping_sync(level=level, all_levels=all_levels, force=force)


def _run_scraping_sync(
    level: ExperienceLevel | None,
    all_levels: bool,
    force: bool,
) -> list[Path]:
    """Run synchronous scraping."""
    settings = get_settings()
    storage = JsonVacancyStorage(settings.raw_data_dir)
    saved_paths: list[Path] = []

    with DouScraper(settings) as scraper:
        snapshots = _collect_snapshots(scraper, level, all_levels)

        for snapshot in snapshots:
            if not force and storage.snapshot_exists(snapshot):
                logger.info(
                    "Snapshot already exists for %s/%s, skipping (use --force)",
                    snapshot.snapshot_date,
                    snapshot.experience_level.value,
                )
                continue
            path = storage.save_snapshot(snapshot)
            saved_paths.append(path)
            logger.info("Saved %d vacancies to %s", snapshot.total, path)

    return saved_paths


async def _run_scraping_async(
    level: ExperienceLevel | None,
    all_levels: bool,
    force: bool,
) -> list[Path]:
    """Run async scraping with aiohttp."""
    settings = get_settings()
    storage = JsonVacancyStorage(settings.raw_data_dir)
    saved_paths: list[Path] = []
    scraper = AsyncDouScraper(settings)

    if all_levels:
        snapshots = await scraper.scrape_all_levels()
    elif level is not None:
        snapshots = [await scraper.scrape(level)]
    else:
        snapshots = [await scraper.scrape(ExperienceLevel.JUNIOR)]

    for snapshot in snapshots:
        if not force and storage.snapshot_exists(snapshot):
            logger.info(
                "Snapshot already exists for %s/%s, skipping (use --force)",
                snapshot.snapshot_date,
                snapshot.experience_level.value,
            )
            continue
        path = storage.save_snapshot(snapshot)
        saved_paths.append(path)
        logger.info("Saved %d vacancies to %s", snapshot.total, path)

    return saved_paths


def _collect_snapshots(scraper: DouScraper, level, all_levels: bool):
    """Collect snapshots from sync scraper."""
    if all_levels:
        return scraper.scrape_all_levels()
    if level is not None:
        return [scraper.scrape(level)]
    return [scraper.scrape(ExperienceLevel.JUNIOR)]


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Scrape Python job vacancies")
    parser.add_argument(
        "--level",
        choices=["junior", "middle", "senior"],
        help="Experience level to scrape",
    )
    parser.add_argument(
        "--all-levels",
        action="store_true",
        help="Scrape all experience levels",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing snapshot for today",
    )
    parser.add_argument(
        "--async",
        dest="use_async",
        action="store_true",
        help="Use async aiohttp scraper",
    )
    args = parser.parse_args()

    exp_level = ExperienceLevel.from_string(args.level) if args.level else None
    paths = run_scraping(
        level=exp_level,
        all_levels=args.all_levels,
        force=args.force,
        use_async=args.use_async,
    )
    print(f"Done. Saved {len(paths)} snapshot(s).")
