"""JSON-based vacancy snapshot storage."""

import json
from datetime import date, datetime
from pathlib import Path

from tech_market_analyzer.domain.interfaces import VacancyStorage
from tech_market_analyzer.domain.models import ExperienceLevel, Vacancy, VacancySnapshot


class JsonVacancyStorage(VacancyStorage):
    """Store and load vacancy snapshots as JSON files.

    File naming convention: ``{date}_{level}.json``
    Example: ``2026-05-29_junior.json``
    """

    def __init__(self, raw_data_dir: Path) -> None:
        """Initialize storage with a target directory.

        Parameters
        ----------
        raw_data_dir : Path
            Directory for raw vacancy JSON files.
        """
        self.raw_data_dir = raw_data_dir
        self.raw_data_dir.mkdir(parents=True, exist_ok=True)

    def _snapshot_filename(self, snapshot: VacancySnapshot) -> str:
        """Build filename for a snapshot."""
        date_str = snapshot.snapshot_date.isoformat()
        level = snapshot.experience_level.value
        return f"{date_str}_{level}.json"

    def save_snapshot(self, snapshot: VacancySnapshot) -> Path:
        """Save snapshot to JSON file."""
        path = self.raw_data_dir / self._snapshot_filename(snapshot)
        payload = {
            "snapshot_date": snapshot.snapshot_date.isoformat(),
            "experience_level": snapshot.experience_level.value,
            "source": snapshot.source,
            "total": snapshot.total,
            "vacancies": [_vacancy_to_dict(v) for v in snapshot.vacancies],
        }
        path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        return path

    def load_snapshot(self, path: Path) -> VacancySnapshot:
        """Load snapshot from JSON file."""
        data = json.loads(path.read_text(encoding="utf-8"))
        vacancies = [_dict_to_vacancy(item) for item in data["vacancies"]]
        return VacancySnapshot(
            vacancies=vacancies,
            experience_level=ExperienceLevel.from_string(data["experience_level"]),
            snapshot_date=date.fromisoformat(data["snapshot_date"]),
            source=data.get("source", "unknown"),
        )

    def list_snapshots(
        self, experience_level: ExperienceLevel | None = None
    ) -> list[Path]:
        """List snapshot files sorted by date descending."""
        pattern = "*.json"
        files = sorted(self.raw_data_dir.glob(pattern), reverse=True)
        if experience_level is None:
            return files
        suffix = f"_{experience_level.value}.json"
        return [f for f in files if f.name.endswith(suffix)]

    def get_latest_snapshot(self, experience_level: ExperienceLevel) -> Path | None:
        """Return the newest snapshot path for a given level."""
        snapshots = self.list_snapshots(experience_level)
        return snapshots[0] if snapshots else None

    def snapshot_exists(self, snapshot: VacancySnapshot) -> bool:
        """Check if a snapshot file already exists for today and level."""
        path = self.raw_data_dir / self._snapshot_filename(snapshot)
        return path.exists()


def _vacancy_to_dict(vacancy: Vacancy) -> dict:
    """Serialize a Vacancy to a JSON-compatible dict."""
    return {
        "id": vacancy.id,
        "title": vacancy.title,
        "company": vacancy.company,
        "description": vacancy.description,
        "experience_level": vacancy.experience_level.value,
        "source": vacancy.source,
        "scraped_at": vacancy.scraped_at.isoformat(),
        "salary": vacancy.salary,
        "views": vacancy.views,
        "applications": vacancy.applications,
        "url": vacancy.url,
    }


def _dict_to_vacancy(data: dict) -> Vacancy:
    """Deserialize a Vacancy from a dict."""
    return Vacancy(
        id=data["id"],
        title=data["title"],
        company=data["company"],
        description=data["description"],
        experience_level=ExperienceLevel.from_string(data["experience_level"]),
        source=data["source"],
        scraped_at=datetime.fromisoformat(data["scraped_at"]),
        salary=data.get("salary"),
        views=data.get("views"),
        applications=data.get("applications"),
        url=data.get("url"),
    )
