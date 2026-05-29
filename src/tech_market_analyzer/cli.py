"""Unified CLI for Tech Market Analyzer."""

import logging
from pathlib import Path
from typing import Optional

import typer

from tech_market_analyzer.analysis.runner import run_analysis, run_history_comparison
from tech_market_analyzer.domain.models import ExperienceLevel
from tech_market_analyzer.scraping.runner import run_scraping

app = typer.Typer(
    name="tech-analyzer",
    help="Scrape Python job vacancies and analyze demanded technologies.",
    no_args_is_help=True,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


@app.command()
def scrape(
    level: Optional[str] = typer.Option(
        None, "--level", "-l", help="junior | middle | senior"
    ),
    all_levels: bool = typer.Option(False, "--all-levels", help="Scrape all levels"),
    force: bool = typer.Option(False, "--force", help="Overwrite today's snapshot"),
) -> None:
    """Scrape vacancies from DOU.ua (independent from analysis)."""
    exp_level = ExperienceLevel.from_string(level) if level else None
    paths = run_scraping(level=exp_level, all_levels=all_levels, force=force)
    typer.echo(f"Saved {len(paths)} snapshot(s).")


@app.command()
def analyze(
    input_file: Optional[Path] = typer.Option(
        None, "--input", "-i", help="Path to raw snapshot JSON"
    ),
    latest: bool = typer.Option(False, "--latest", help="Analyze latest snapshot"),
    level: str = typer.Option("junior", "--level", "-l"),
    top_n: int = typer.Option(15, "--top-n"),
) -> None:
    """Analyze technology demand from saved snapshots (no HTTP requests)."""
    stats_path, chart_path = run_analysis(
        input_path=input_file,
        latest=latest,
        level=ExperienceLevel.from_string(level),
        top_n=top_n,
    )
    typer.echo(f"Stats: {stats_path}")
    typer.echo(f"Chart: {chart_path}")


@app.command()
def history(
    older: str = typer.Argument(..., help="Older date (YYYY-MM-DD)"),
    newer: str = typer.Argument(..., help="Newer date (YYYY-MM-DD)"),
    level: str = typer.Option("junior", "--level", "-l"),
) -> None:
    """Compare technology trends between two snapshot dates."""
    run_history_comparison(older, newer, ExperienceLevel.from_string(level))


@app.command()
def pipeline(
    all_levels: bool = typer.Option(True, "--all-levels/--single-level"),
    force: bool = typer.Option(False, "--force"),
    top_n: int = typer.Option(15, "--top-n"),
) -> None:
    """Run full pipeline: scrape → analyze for all levels."""
    levels = list(ExperienceLevel) if all_levels else [ExperienceLevel.JUNIOR]

    for exp_level in levels:
        typer.echo(f"\n=== {exp_level.value.upper()} ===")
        paths = run_scraping(level=exp_level, force=force)
        if not paths:
            typer.echo(f"No new snapshot for {exp_level.value}, trying latest...")
        run_analysis(latest=True, level=exp_level, top_n=top_n)

    typer.echo("\nPipeline complete.")


if __name__ == "__main__":
    app()
