"""Project path constants."""

from pathlib import Path


def _find_project_root() -> Path:
    """Locate project root via pyproject.toml (editable + site-packages)."""
    start = Path(__file__).resolve().parent
    for candidate in (start, *start.parents):
        if (candidate / "pyproject.toml").exists():
            return candidate
    return start.parents[2]


PROJECT_ROOT = _find_project_root()
CONFIG_DIR = PROJECT_ROOT / "config"
