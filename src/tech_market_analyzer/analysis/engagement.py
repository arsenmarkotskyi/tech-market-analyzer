"""Analyze vacancy engagement metrics (applications) when available."""

import json
import logging
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import pandas as pd

from tech_market_analyzer.analysis.technology_counter import _matches_technology
from tech_market_analyzer.domain.models import ExperienceLevel, Vacancy, VacancySnapshot
from tech_market_analyzer.settings import load_technologies

logger = logging.getLogger(__name__)


@dataclass
class EngagementReport:
    """Summary of engagement analysis for a snapshot."""

    total_vacancies: int
    with_applications: int
    correlations: dict[str, float | None]
    top_low_competition: list[dict]


def _vacancy_technology_count(vacancy: Vacancy, technologies: list[str]) -> int:
    """Count configured technologies mentioned in a vacancy description."""
    text = vacancy.description.lower()
    return sum(1 for tech in technologies if _matches_technology(text, tech))


def analyze_engagement(
    snapshot: VacancySnapshot,
    technologies: list[str] | None = None,
) -> EngagementReport:
    """Correlate applications with technologies and description length."""
    tech_list = technologies or load_technologies()
    rows = []

    for vacancy in snapshot.vacancies:
        rows.append(
            {
                "id": vacancy.id,
                "title": vacancy.title,
                "location": vacancy.location,
                "applications": vacancy.applications,
                "tech_count": _vacancy_technology_count(vacancy, tech_list),
                "description_len": len(vacancy.description),
            }
        )

    df = pd.DataFrame(rows)
    with_apps = int(df["applications"].notna().sum()) if not df.empty else 0

    correlations: dict[str, float | None] = {
        "applications_vs_tech_count": None,
        "applications_vs_description_len": None,
    }

    if with_apps >= 3:
        correlations["applications_vs_tech_count"] = _safe_corr(
            df, "applications", "tech_count"
        )
        correlations["applications_vs_description_len"] = _safe_corr(
            df, "applications", "description_len"
        )

    top_low = []
    if with_apps >= 1:
        subset = df.dropna(subset=["applications"]).copy()
        if not subset.empty:
            top_low = (
                subset.sort_values("applications", ascending=True)
                .head(5)[["id", "title", "location", "applications", "tech_count"]]
                .to_dict(orient="records")
            )

    return EngagementReport(
        total_vacancies=len(snapshot.vacancies),
        with_applications=with_apps,
        correlations=correlations,
        top_low_competition=top_low,
    )


def _safe_corr(df: pd.DataFrame, col_a: str, col_b: str) -> float | None:
    """Compute Pearson correlation when enough non-null pairs exist."""
    subset = df[[col_a, col_b]].dropna()
    if len(subset) < 3:
        return None
    if subset[col_a].std() == 0 or subset[col_b].std() == 0:
        return None
    value = float(subset[col_a].corr(subset[col_b]))
    if pd.isna(value):
        return None
    return round(value, 4)


def save_engagement_report(
    report: EngagementReport,
    output_path: Path,
    snapshot_date: date,
    experience_level: ExperienceLevel,
) -> Path:
    """Save engagement analysis report as JSON."""
    payload = {
        "snapshot_date": snapshot_date.isoformat(),
        "experience_level": experience_level.value,
        "total_vacancies": report.total_vacancies,
        "with_applications": report.with_applications,
        "correlations": report.correlations,
        "top_low_competition": report.top_low_competition,
        "note": (
            "DOU.ua exposes applications on some vacancy pages only. "
            "Re-run after scraping fresh snapshots."
            if report.with_applications == 0
            else None
        ),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return output_path
