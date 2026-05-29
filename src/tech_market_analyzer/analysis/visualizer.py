"""Generate charts from technology statistics."""

from pathlib import Path

import matplotlib.pyplot as plt

from tech_market_analyzer.domain.models import ExperienceLevel, TechnologyStats


def create_bar_chart(
    stats: list[TechnologyStats],
    experience_level: ExperienceLevel,
    output_path: Path,
    top_n: int = 15,
) -> Path:
    """Create a horizontal bar chart of top demanded technologies.

    Parameters
    ----------
    stats : list[TechnologyStats]
        Technology statistics (pre-sorted by count).
    experience_level : ExperienceLevel
        Level label for chart title.
    output_path : Path
        Destination PNG file path.
    top_n : int
        Number of top technologies to display.

    Returns
    -------
    Path
        Path to the saved chart.
    """
    top_stats = stats[:top_n]
    if not top_stats:
        _create_empty_chart(experience_level, output_path)
        return output_path

    technologies = [s.technology for s in top_stats]
    counts = [s.count for s in top_stats]

    fig, ax = plt.subplots(figsize=(10, max(6, len(technologies) * 0.4)))
    bars = ax.barh(technologies[::-1], counts[::-1], color="#4C72B0")

    ax.set_xlabel("Number of vacancies")
    ax.set_title(
        f"Top {len(top_stats)} Technologies — {experience_level.value.capitalize()}"
        f" ({top_stats[0].snapshot_date})"
    )

    for bar, stat in zip(bars, top_stats[::-1]):
        ax.text(
            bar.get_width() + 0.3,
            bar.get_y() + bar.get_height() / 2,
            f"{stat.count} ({stat.percentage}%)",
            va="center",
            fontsize=9,
        )

    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return output_path


def _create_empty_chart(
    experience_level: ExperienceLevel, output_path: Path
) -> None:
    """Save a placeholder chart when no data is available."""
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.text(
        0.5,
        0.5,
        "No technology data available",
        ha="center",
        va="center",
        fontsize=14,
    )
    ax.set_title(f"Technologies — {experience_level.value.capitalize()}")
    ax.axis("off")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
