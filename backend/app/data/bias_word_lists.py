"""
Seed word lists for JD language bias scoring.

These are starter lists based on categories used in published gendered-language
research (e.g. Gaucher, Friesen & Kay, "Evidence That Gendered Wording in Job
Advertisements Exists and Sustains Gender Inequality," J. Personality & Social
Psychology, 2011) and commonly cited exclusionary-language guides.

TODO before production use:
  - Expand each list substantially (aim for 150-300 terms per category)
  - Source from a proper published dataset rather than this seed list
  - Consider stemming/lemmatization so "aggressively" also matches "aggressive"
  - Age-coded and ability-coded lists below are minimal starter sets - expand
"""

MASCULINE_CODED = {
    "active", "adventurous", "aggressive", "ambitious", "analytical",
    "assertive", "athletic", "autonomous", "boast", "challenging",
    "competitive", "confident", "courageous", "decide", "decisive",
    "determined", "dominant", "driven", "fearless", "fight", "force",
    "hierarchical", "independent", "individualistic", "lead", "leader",
    "objective", "outspoken", "persist", "principles", "reckless",
    "self-reliant", "self-sufficient", "stubborn", "superior",
}

FEMININE_CODED = {
    "affectionate", "collaborate", "commit", "communal", "compassionate",
    "connect", "considerate", "cooperative", "dependable", "emotional",
    "empathetic", "enthusiastic", "flexible", "gentle", "honest",
    "interpersonal", "kind", "loyal", "nurture", "pleasant", "polite",
    "responsive", "sensitive", "supportive", "sympathetic", "together",
    "trust", "understanding", "warm", "yield",
}

AGE_CODED_YOUNGER = {
    "digital native", "energetic", "fresh graduate", "fresh perspective",
    "high-energy", "recent graduate", "young", "youthful", "vibrant team",
    "millennial", "gen z",
}

AGE_CODED_OLDER = {
    "seasoned", "mature", "years of experience required", "veteran",
}

ABLEIST_OR_EXCLUSIONARY = {
    "must be able to stand for long periods", "must have own transportation",
    "no accommodations", "perfect health", "physically demanding",
    "rockstar", "ninja", "superhero", "work hard play hard",
    "unlimited availability", "must be willing to work weekends without exception",
}

EXPERIENCE_PROXY_FLAGS = {
    # These aren't inherently biased but correlate with excluding career-changers,
    # parents returning to work, and older/younger candidates unfairly.
    "10+ years", "digital native", "recent graduate only",
    "must have started coding before age", "culture fit",
}

CATEGORY_LABELS = {
    "masculine_coded": MASCULINE_CODED,
    "feminine_coded": FEMININE_CODED,
    "age_coded_younger": AGE_CODED_YOUNGER,
    "age_coded_older": AGE_CODED_OLDER,
    "ableist_or_exclusionary": ABLEIST_OR_EXCLUSIONARY,
    "experience_proxy": EXPERIENCE_PROXY_FLAGS,
}
