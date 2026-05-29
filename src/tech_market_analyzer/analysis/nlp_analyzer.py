"""NLP-based word frequency analysis without a technology config."""

import json
import logging
import re
from collections import Counter
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from tech_market_analyzer.domain.models import ExperienceLevel, VacancySnapshot

logger = logging.getLogger(__name__)

# Extra stop words common in job postings (EN + UA)
EXTRA_STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "you",
    "your",
    "our",
    "will",
    "are",
    "have",
    "from",
    "this",
    "that",
    "not",
    "all",
    "work",
    "team",
    "company",
    "experience",
    "skills",
    "role",
    "job",
    "developer",
    "development",
    "engineer",
    "looking",
    "required",
    "requirements",
    "ability",
    "knowledge",
    "years",
    "year",
    "plus",
    "etc",
    "including",
    "using",
    "use",
    "also",
    "well",
    "must",
    "should",
    "can",
    "who",
    "what",
    "how",
    "about",
    "more",
    "than",
    "into",
    "such",
    "other",
    "any",
    "one",
    "two",
    "three",
    "new",
    "join",
    "remote",
    "full",
    "time",
    "part",
    "в",
    "і",
    "та",
    "на",
    "з",
    "до",
    "для",
    "що",
    "як",
    "ми",
    "ви",
    "або",
    "але",
    "це",
    "від",
    "про",
    "буде",
    "робота",
    "досвід",
    "років",
    "рік",
    "компанія",
    "команда",
    "розробник",
    "вакансія",
}


@dataclass
class WordStat:
    """Word frequency statistic."""

    word: str
    count: int
    percentage: float


def _tokenize(text: str) -> list[str]:
    """Tokenize text into lowercase alphabetic words."""
    return re.findall(r"[a-zA-Z][a-zA-Z0-9+#.-]{1,}", text.lower())


def _load_stopwords() -> set[str]:
    """Load NLTK stopwords with graceful fallback."""
    try:
        import nltk

        try:
            nltk.download("stopwords", quiet=True)
        except Exception:
            logger.warning("Could not download NLTK stopwords; using built-in list")

        from nltk.corpus import stopwords

        return set(stopwords.words("english")) | EXTRA_STOPWORDS
    except (ImportError, LookupError):
        logger.warning("nltk stopwords unavailable; using built-in stopword list only")
        return EXTRA_STOPWORDS


def analyze_word_frequency(
    snapshot: VacancySnapshot,
    top_n: int = 30,
    min_word_length: int = 3,
) -> list[WordStat]:
    """Count word frequencies across vacancy descriptions without a tech config."""
    stopwords = _load_stopwords()
    counter: Counter[str] = Counter()

    for vacancy in snapshot.vacancies:
        for token in _tokenize(vacancy.description):
            if len(token) < min_word_length or token in stopwords:
                continue
            counter[token] += 1

    total_tokens = sum(counter.values()) or 1
    stats = [
        WordStat(
            word=word,
            count=count,
            percentage=round(count / total_tokens * 100, 2),
        )
        for word, count in counter.most_common(top_n)
    ]
    return stats


def save_word_stats(
    stats: list[WordStat],
    output_path: Path,
    snapshot_date: date,
    experience_level: ExperienceLevel,
) -> Path:
    """Persist NLP word stats as JSON."""
    payload = {
        "snapshot_date": snapshot_date.isoformat(),
        "experience_level": experience_level.value,
        "words": [
            {"word": s.word, "count": s.count, "percentage": s.percentage}
            for s in stats
        ],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return output_path


def create_wordcloud(
    stats: list[WordStat],
    output_path: Path,
    experience_level: ExperienceLevel,
) -> Path | None:
    """Generate a word cloud image from word frequency stats."""
    try:
        from wordcloud import WordCloud
    except ImportError:
        logger.warning("wordcloud not installed; skip image generation")
        return None

    if not stats:
        return None

    frequencies = {s.word: s.count for s in stats}
    cloud = WordCloud(
        width=1000,
        height=500,
        background_color="white",
        colormap="viridis",
    ).generate_from_frequencies(frequencies)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    cloud.to_file(str(output_path))
    logger.info("Saved word cloud: %s (%s)", output_path, experience_level.value)
    return output_path
