"""CLI entry point for the scraping module (runs independently)."""

import logging
from pathlib import Path

from tech_market_analyzer.domain.models import ExperienceLevel
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
) -> list[Path]:
    """Run scraping and save snapshots to disk.

    Parameters
    ----------
    level : ExperienceLevel | None
        Single experience level to scrape.
    all_levels : bool
        If True, scrape all configured levels.
    force : bool
        If True, overwrite existing snapshots for today.

    Returns
    -------
    list[Path]
        Paths to saved snapshot files.
    """
    settings = get_settings()
    storage = JsonVacancyStorage(settings.raw_data_dir)
    saved_paths: list[Path] = []

    with DouScraper(settings) as scraper:
        if all_levels:
            snapshots = scraper.scrape_all_levels()
        elif level is not None:
            snapshots = [scraper.scrape(level)]
        else:
            snapshots = [scraper.scrape(ExperienceLevel.JUNIOR)]

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
    args = parser.parse_args()

    exp_level = ExperienceLevel.from_string(args.level) if args.level else None
    paths = run_scraping(level=exp_level, all_levels=args.all_levels, force=args.force)
    print(f"Done. Saved {len(paths)} snapshot(s).")
