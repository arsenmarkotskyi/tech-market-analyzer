"""Centralized runtime configuration for the project."""

from pathlib import Path

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from tech_market_analyzer._paths import CONFIG_DIR, PROJECT_ROOT


class Settings(BaseSettings):
    """Application settings loaded from environment variables and defaults."""

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    base_url: str = "https://jobs.dou.ua"
    category: str = "Python"
    request_delay_seconds: float = 1.5
    max_pages: int = 10
    async_max_concurrency: int = 3
    user_agent: str = "TechMarketAnalyzer/0.1"

    raw_data_dir: Path = Field(default=PROJECT_ROOT / "data" / "raw")
    results_dir: Path = Field(default=PROJECT_ROOT / "data" / "results")
    technologies_config: Path = Field(default=CONFIG_DIR / "technologies.yaml")

    experience_levels: list[str] = Field(
        default_factory=lambda: ["junior", "middle", "senior"]
    )

    def ensure_dirs(self) -> None:
        """Create data directories if they do not exist."""
        self.raw_data_dir.mkdir(parents=True, exist_ok=True)
        self.results_dir.mkdir(parents=True, exist_ok=True)


def load_technologies(config_path: Path | None = None) -> list[str]:
    """Load technology keywords from YAML config file.

    Parameters
    ----------
    config_path : Path | None
        Path to technologies YAML. Defaults to ``config/technologies.yaml``.

    Returns
    -------
    list[str]
        List of technology names to search for in vacancy descriptions.
    """
    path = config_path or CONFIG_DIR / "technologies.yaml"
    with path.open(encoding="utf-8") as file:
        data = yaml.safe_load(file)
    return data.get("technologies", [])


def get_settings() -> Settings:
    """Return a configured Settings instance with directories ensured."""
    settings = Settings()
    settings.ensure_dirs()
    return settings
