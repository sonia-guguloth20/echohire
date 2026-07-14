"""
JD Language Bias Analyzer.

Phase 1 (this file): word-list based scoring. Fast, explainable, zero
training data needed - good enough to ship an MVP and start collecting
labeled data.

Phase 2 (upgrade path, not built yet): fine-tune a small transformer
(e.g. distilbert-base-uncased) as a binary/multi-label classifier on a
labeled corpus of JD sentences, using this word-list output as weak
labels to bootstrap training data. Swap `score_job_description` internals
without changing the public interface below, so routers/tests don't break.
"""

import re
from dataclasses import dataclass, field

from app.data.bias_word_lists import CATEGORY_LABELS

# Rough severity weighting per category - tune based on what your users
# actually care about (legal risk vs. inclusivity optimization)
CATEGORY_WEIGHTS = {
    "masculine_coded": 1.0,
    "feminine_coded": 1.0,
    "age_coded_younger": 1.5,
    "age_coded_older": 1.5,
    "ableist_or_exclusionary": 2.0,
    "experience_proxy": 1.2,
}

SUGGESTIONS = {
    "masculine_coded": "Consider a more neutral synonym - masculine-coded words like this correlate with fewer women applying (Gaucher, Friesen & Kay, 2011).",
    "feminine_coded": "Feminine-coded language isn't inherently bad, but heavy skew in either direction narrows your applicant pool.",
    "age_coded_younger": "This phrase can be read as an age preference and may deter older applicants (and raises ADEA concerns in the US).",
    "age_coded_older": "This phrase can be read as an age preference for older candidates - consider whether it's necessary or could be reframed as a skill requirement.",
    "ableist_or_exclusionary": "This phrasing may exclude candidates with disabilities without being a genuine job requirement. Confirm it's an essential function before keeping it.",
    "experience_proxy": "This can act as a proxy that filters out qualified non-traditional candidates (career changers, parents returning to work). Consider whether the underlying skill could be stated directly instead.",
}


@dataclass
class FlaggedPhrase:
    phrase: str
    category: str
    suggestion: str
    position: int


@dataclass
class JDAnalysisResult:
    bias_score: float  # 0 (clean) to 100 (heavily biased)
    flagged_phrases: list = field(default_factory=list)
    category_counts: dict = field(default_factory=dict)


def _tokenize_lower(text: str) -> str:
    return text.lower()


def score_job_description(jd_text: str) -> JDAnalysisResult:
    text_lower = _tokenize_lower(jd_text)
    word_count = max(len(jd_text.split()), 1)

    flagged: list[FlaggedPhrase] = []
    category_counts: dict[str, int] = {cat: 0 for cat in CATEGORY_LABELS}
    weighted_hits = 0.0

    for category, terms in CATEGORY_LABELS.items():
        for term in terms:
            # word-boundary match, handles multi-word phrases too
            pattern = r"\b" + re.escape(term) + r"\b"
            for match in re.finditer(pattern, text_lower):
                flagged.append(
                    FlaggedPhrase(
                        phrase=term,
                        category=category,
                        suggestion=SUGGESTIONS[category],
                        position=match.start(),
                    )
                )
                category_counts[category] += 1
                weighted_hits += CATEGORY_WEIGHTS[category]

    # Normalize by JD length so a long JD isn't unfairly penalized for having
    # more total words. Scale to a 0-100 score, cap at 100.
    density = weighted_hits / word_count * 100
    bias_score = min(round(density * 12, 1), 100.0)  # 12x multiplier tuned so a
    # ~600-word JD with ~6 flagged terms lands around 40-50 (moderate). Recalibrate
    # once you have real JDs to test against.

    flagged.sort(key=lambda f: f.position)

    return JDAnalysisResult(
        bias_score=bias_score,
        flagged_phrases=[
            {"phrase": f.phrase, "category": f.category, "suggestion": f.suggestion}
            for f in flagged
        ],
        category_counts=category_counts,
    )
