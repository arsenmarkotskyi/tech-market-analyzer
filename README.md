# Tech Market Analyzer

A service that scrapes public Python developer vacancies and analyzes technology demand on the job market.

## Features

- **Scraping** — collect vacancies from [jobs.dou.ua](https://jobs.dou.ua) (public data, no authentication)
- **Analysis** — count technology mentions in vacancy descriptions
- **Visualization** — bar charts of top technologies
- **History** — save snapshots to compare trends over time
- **Experience levels** — separate analysis for junior / middle / senior
- **Independent modules** — scraping and analysis run separately (SRP)

## Project structure

```
tech-market-analyzer/
├── config/
│   └── technologies.yaml     # Technology keywords to search for
├── docs/
│   └── images/               # Chart screenshots for README
├── src/tech_market_analyzer/
│   ├── settings.py           # Pydantic Settings
│   ├── domain/               # Models and interfaces
│   ├── scraping/             # Part 1: data collection
│   ├── analysis/             # Part 2: analysis
│   ├── storage/              # JSON + results
│   └── cli.py                # Single entry point
├── data/
│   ├── raw/                  # Vacancy JSON snapshots
│   └── results/              # Charts + statistics
└── tests/
```

## Installation

```bash
git clone https://github.com/arsenmarkotskyi/tech-market-analyzer.git
cd tech-market-analyzer

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install -e ".[dev]"
cp .env.example .env
```

## Usage

### Full pipeline

```bash
# scrape → analyze for junior, middle, senior
tech-analyzer pipeline --all-levels --force
```

Example output (snapshot 2026-05-29):

| Level | DOU filter | Vacancies | Top 3 technologies |
|-------|------------|-----------|-------------------|
| junior | `exp=0-1` | 7 | Docker, Git, PostgreSQL |
| middle | `exp=1-3` | 20 | PostgreSQL, Docker, FastAPI |
| senior | `exp=3-5` + `exp=5plus` | 40 | CI/CD, Docker, PostgreSQL |

Output files: `data/raw/2026-05-29_{level}.json` and `data/results/2026-05-29/{level}_*`.

### Scraping only

```bash
# Single level
tech-analyzer scrape --level senior

# All levels
tech-analyzer scrape --all-levels

# Overwrite today's snapshot
tech-analyzer scrape --all-levels --force
```

### Analysis only

```bash
# Latest snapshot
tech-analyzer analyze --latest --level senior

# Specific file
tech-analyzer analyze --input data/raw/2026-05-29_senior.json
```

### History comparison

```bash
tech-analyzer history 2026-05-20 2026-05-29 --level senior
```

## Example results

After analysis, `data/results/YYYY-MM-DD/` contains:

- `{level}_bar_chart.png` — top technologies chart
- `{level}_stats.json` — statistics in JSON

### Market analysis (snapshot 2026-05-29, [jobs.dou.ua](https://jobs.dou.ua))

**Key findings:**

- **Docker** and **PostgreSQL** show the steadiest demand — top 3 at every experience level.
- **CI/CD** grows sharply with seniority: 57% (junior) → 15% (middle) → **53% (senior)** — #1 for senior roles.
- **FastAPI** is most popular among middle (40%), while **Django** is stronger for senior (30%).
- The junior market is small (7 vacancies) but already expects DevOps basics: Docker (86%), Git (86%), AWS (57%).

**Charts by level:**

| Junior (7) | Middle (20) | Senior (40) |
|:---:|:---:|:---:|
| ![Junior](docs/images/junior_bar_chart.png) | ![Middle](docs/images/middle_bar_chart.png) | ![Senior](docs/images/senior_bar_chart.png) |

### Top 5 technologies by level

**Junior** (`exp=0-1`, 7 vacancies):

```
   1. Docker        6  (85.7%)
   2. Git           6  (85.7%)
   3. PostgreSQL    5  (71.4%)
   4. AWS           4  (57.1%)
   5. CI/CD         4  (57.1%)
```

**Middle** (`exp=1-3`, 20 vacancies):

```
   1. PostgreSQL    9  (45.0%)
   2. Docker        9  (45.0%)
   3. FastAPI       8  (40.0%)
   4. Git           8  (40.0%)
   5. Linux         8  (40.0%)
```

**Senior** (`exp=3-5` + `exp=5plus`, 40 vacancies):

```
   1. CI/CD        21  (52.5%)
   2. Docker       19  (47.5%)
   3. PostgreSQL   18  (45.0%)
   4. AWS          16  (40.0%)
   5. Redis        14  (35.0%)
```

> **DOU.ua note:** category filter uses `?category=Python` (not `search`).
> Experience levels use ranges: `exp=0-1` (junior), `exp=1-3` (middle),
> `exp=3-5` and `exp=5plus` (senior — both filters, results merged).

## Configuration

| Parameter | File | Description |
|-----------|------|-------------|
| Technologies | `config/technologies.yaml` | Keywords to search for |
| DOU category | `.env` → `CATEGORY` | Job category (default `Python`) |
| HTTP delay | `.env` → `REQUEST_DELAY_SECONDS` | Delay between requests |
| Max pages | `.env` → `MAX_PAGES` | Pagination page limit |

## Tests

```bash
pytest
```

### Pre-commit (local)

```bash
pip install -e ".[dev]"
pre-commit install
pre-commit run --all-files
```

CI (GitHub Actions) runs `flake8`, `black`, `isort`, and `pytest` on Python 3.11 and 3.12 on every push/PR.

## Optional features (implemented)

### Async scraping (`aiohttp`)

```bash
pip install -e ".[async]"
tech-analyzer scrape --level junior --async --force
tech-analyzer pipeline --all-levels --async
```

Parallel detail-page fetching with `ASYNC_MAX_CONCURRENCY` (default 3).

### NLP analysis without config (`nltk` + `wordcloud`)

```bash
pip install -e ".[nlp]"
tech-analyzer analyze-nlp --latest --level senior
```

Produces `{level}_nlp_stats.json` and `{level}_wordcloud.png` without `technologies.yaml`.

### Applications correlation analysis

```bash
tech-analyzer analyze-engagement --latest --level senior
```

> **Note:** DOU.ua shows application counts only on some vacancy pages.
> Location (`remote`, city name) is parsed from the listing page.

## Disclaimer

This project collects **public** information only, without authentication. Respect the site's `robots.txt` and Terms of Service. Use rate limiting to avoid overloading the server.

## License

MIT
