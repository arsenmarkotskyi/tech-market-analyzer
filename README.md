# Tech Market Analyzer

Сервіс для збору публічних вакансій Python-розробників та аналізу попиту на технології на ринку праці.

## Можливості

- **Scraping** — збір вакансій з [jobs.dou.ua](https://jobs.dou.ua) (публічні дані, без авторизації)
- **Analysis** — підрахунок згадок технологій у описах вакансій
- **Візуалізація** — bar chart топ-технологій
- **Історія** — збереження знімків для порівняння трендів у часі
- **Рівні досвіду** — окремий аналіз для junior / middle / senior
- **Незалежні модулі** — scraping і analysis запускаються окремо (SRP)

## Структура проекту

```
tech-market-analyzer/
├── config/
│   └── technologies.yaml     # Список технологій для пошуку
├── docs/
│   └── images/               # Скріншоти діаграм для README
├── src/tech_market_analyzer/
│   ├── settings.py           # Pydantic Settings
│   ├── domain/               # Моделі та інтерфейси
│   ├── scraping/             # Частина 1: збір даних
│   ├── analysis/             # Частина 2: аналіз
│   ├── storage/              # JSON + результати
│   └── cli.py                # Єдина точка входу
├── data/
│   ├── raw/                  # JSON знімки вакансій
│   └── results/              # Діаграми + статистика
└── tests/
```

## Встановлення

```bash
git clone https://github.com/arsenmarkotskyi/tech-market-analyzer.git
cd tech-market-analyzer

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install -e ".[dev]"
cp .env.example .env
```

## Використання

### Повний pipeline

```bash
tech-analyzer pipeline --all-levels
```

### Окремо: Scraping

```bash
# Один рівень
tech-analyzer scrape --level senior

# Всі рівні
tech-analyzer scrape --all-levels

# Перезаписати сьогоднішній знімок
tech-analyzer scrape --all-levels --force
```

### Окремо: Analysis

```bash
# Останній знімок
tech-analyzer analyze --latest --level senior

# Конкретний файл
tech-analyzer analyze --input data/raw/2026-05-29_senior.json
```

### Порівняння історії

```bash
tech-analyzer history 2026-05-20 2026-05-29 --level senior
```

## Приклад результату

Після аналізу в `data/results/YYYY-MM-DD/` з'являться:

- `{level}_bar_chart.png` — діаграма топ-технологій
- `{level}_stats.json` — статистика у JSON

### Діаграма (senior, 2026-05-29, 20 вакансій)

![Top technologies — Senior](docs/images/senior_bar_chart.png)

### Топ-10 технологій (вивід CLI)

```
Top 10 technologies:
   1. CI/CD                  13  (65.0%)
   2. AWS                    11  (55.0%)
   3. Docker                  8  (40.0%)
   4. REST                    8  (40.0%)
   5. Azure                   6  (30.0%)
   6. React                   6  (30.0%)
   7. Django                  5  (25.0%)
   8. Flask                   5  (25.0%)
   9. PostgreSQL              5  (25.0%)
  10. Redis                   5  (25.0%)
```

> **Примітка про DOU.ua:** фільтр категорії використовує `?category=Python` (не `search`).
> Для рівнів досвіду — `exp=0` (junior), `exp=1` (middle), `exp=5plus` (senior).
> На момент збору даних junior/middle можуть повертати 0 вакансій — це залежить від поточного ринку, а не від парсера.

## Конфігурація

| Параметр | Файл | Опис |
|----------|------|------|
| Технології | `config/technologies.yaml` | Ключові слова для пошуку |
| Категорія DOU | `.env` → `CATEGORY` | Категорія вакансій (за замовч. `Python`) |
| HTTP delay | `.env` → `REQUEST_DELAY_SECONDS` | Затримка між запитами |
| Max pages | `.env` → `MAX_PAGES` | Ліміт сторінок пагінації |

## Тести

```bash
pytest
```

## Майбутні покращення (optional)

- Async scraping з `aiohttp`
- NLP-аналіз без config через `nltk` + `wordcloud`
- Кореляційний аналіз views/applications

## Disclaimer

Проект збирає лише **публічну** інформацію без авторизації. Дотримуйтесь `robots.txt` та Terms of Service сайту. Використовуйте rate limiting, щоб не перевантажувати сервер.

## Ліцензія

MIT
