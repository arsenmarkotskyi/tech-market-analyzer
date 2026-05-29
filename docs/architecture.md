# Architecture

## Overview

Tech Market Analyzer follows Clean Architecture with strict separation between scraping and analysis.

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  Scraping   │────▶│  data/raw/   │────▶│  Analysis   │
│  (HTTP)     │     │  *.json      │     │  (local)    │
└─────────────┘     └──────────────┘     └──────┬──────┘
                                                 │
                                                 ▼
                                          ┌─────────────┐
                                          │data/results/│
                                          │ PNG + JSON  │
                                          └─────────────┘
```

## Layers

| Layer | Package | Responsibility |
|-------|---------|----------------|
| Domain | `domain/` | Models, ABC interfaces — no I/O |
| Scraping | `scraping/` | HTTP fetch, HTML parse |
| Analysis | `analysis/` | Tech counting, charts, history |
| Storage | `storage/` | JSON persistence |
| CLI | `cli.py` | User-facing commands |

## Independence Contract

- **Scraping** writes to `data/raw/` and never imports analysis code.
- **Analysis** reads from `data/raw/` and never makes HTTP requests.
- Both modules can be run via their own `runner.py` or through unified `cli.py`.

## Data Flow

1. `DouScraper.scrape(level)` → `VacancySnapshot`
2. `JsonVacancyStorage.save_snapshot()` → `data/raw/{date}_{level}.json`
3. `TechnologyCounter.analyze()` → `list[TechnologyStats]`
4. `FileResultsStorage.save_chart()` → `data/results/{date}/{level}_bar_chart.png`

## Extension Points

- Add new scraper: implement `Scraper` ABC (e.g. `work_ua_scraper.py`)
- Add NLP mode: implement alternative `TechnologyAnalyzer` without config list
- Add async: subclass `BaseScraper` with `aiohttp`
