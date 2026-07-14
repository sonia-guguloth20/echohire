"""
Outcome Bias Statistics Engine.

Answers: "Does a candidate's self-reported protected attribute correlate
with their interview outcome, controlling for round number and role?"

Two methods, used together:

1. Fisher's Exact Test - per attribute-category, 2x2 contingency table of
   (attribute value) x (advanced/rejected). Good for small-to-medium samples,
   doesn't assume normality. This is the "quick proof" number.

2. Logistic regression - outcome ~ attribute + department + round_number.
   Lets you control for confounders (e.g. maybe a department just has a
   harder bar, not a biased one) and gives you an odds ratio + p-value per
   attribute, which is what a legal/HR audience actually wants to see.

Both require a minimum cohort size (settings.min_cohort_size) before running,
to avoid drawing conclusions from tiny samples and to avoid re-identifying
individuals in small groups.
"""

from dataclasses import dataclass

import pandas as pd
from scipy.stats import fisher_exact
import statsmodels.api as sm
import statsmodels.formula.api as smf

from app.config import settings


@dataclass
class FisherResult:
    attribute: str
    group_a: str
    group_b: str
    odds_ratio: float
    p_value: float
    advance_rate_a: float
    advance_rate_b: float
    sample_size_a: int
    sample_size_b: int
    significant: bool  # p < 0.05


@dataclass
class LogisticResult:
    attribute: str
    coefficient: float
    odds_ratio: float
    p_value: float
    significant: bool
    n_observations: int


@dataclass
class BiasAuditResult:
    fisher_tests: list
    logistic_summary: LogisticResult | None
    warnings: list
    sufficient_sample: bool


def _advanced_flag(outcome: str) -> int:
    return 1 if outcome in ("advanced", "offered") else 0


def run_fisher_tests(df: pd.DataFrame, attribute_col: str) -> list:
    """
    df must have columns: [attribute_col, 'outcome'].
    Runs pairwise Fisher's Exact Test between each pair of attribute values.
    """
    results = []
    df = df.dropna(subset=[attribute_col])
    df["advanced"] = df["outcome"].apply(_advanced_flag)

    groups = df[attribute_col].unique().tolist()
    if len(groups) < 2:
        return results

    for i in range(len(groups)):
        for j in range(i + 1, len(groups)):
            group_a, group_b = groups[i], groups[j]
            sub_a = df[df[attribute_col] == group_a]
            sub_b = df[df[attribute_col] == group_b]

            if len(sub_a) < settings.min_cohort_size or len(sub_b) < settings.min_cohort_size:
                continue

            a_adv = sub_a["advanced"].sum()
            a_rej = len(sub_a) - a_adv
            b_adv = sub_b["advanced"].sum()
            b_rej = len(sub_b) - b_adv

            table = [[a_adv, a_rej], [b_adv, b_rej]]
            odds_ratio, p_value = fisher_exact(table)

            results.append(
                FisherResult(
                    attribute=attribute_col,
                    group_a=str(group_a),
                    group_b=str(group_b),
                    odds_ratio=round(float(odds_ratio), 3),
                    p_value=round(float(p_value), 4),
                    advance_rate_a=round(a_adv / len(sub_a), 3),
                    advance_rate_b=round(b_adv / len(sub_b), 3),
                    sample_size_a=len(sub_a),
                    sample_size_b=len(sub_b),
                    significant=p_value < 0.05,
                )
            )
    return results


def run_logistic_regression(df: pd.DataFrame, attribute_col: str) -> LogisticResult | None:
    """
    Fits: advanced ~ C(attribute) + C(department) + round_number
    Controls for department and round number so we're not attributing a
    department-wide difficulty bar to bias in a single attribute.
    """
    df = df.dropna(subset=[attribute_col, "department", "round_number"]).copy()
    df["advanced"] = df["outcome"].apply(_advanced_flag)

    if len(df) < settings.min_cohort_size * 2:
        return None
    if df[attribute_col].nunique() < 2:
        return None

    formula = f'advanced ~ C({attribute_col}) + C(department) + round_number'
    try:
        model = smf.logit(formula, data=df).fit(disp=0)
    except Exception:
        return None

    # grab the first non-reference coefficient for the attribute
    target_params = [p for p in model.params.index if attribute_col in p]
    if not target_params:
        return None
    param = target_params[0]

    coef = model.params[param]
    p_value = model.pvalues[param]

    return LogisticResult(
        attribute=attribute_col,
        coefficient=round(float(coef), 4),
        odds_ratio=round(float(pd.Series([coef]).apply(lambda x: __import__("math").exp(x)).iloc[0]), 3),
        p_value=round(float(p_value), 4),
        significant=p_value < 0.05,
        n_observations=len(df),
    )


def run_full_audit(df: pd.DataFrame, attribute_col: str) -> BiasAuditResult:
    warnings = []
    if df.empty:
        return BiasAuditResult(fisher_tests=[], logistic_summary=None,
                                warnings=["No interview data provided."], sufficient_sample=False)

    value_counts = df[attribute_col].value_counts()
    sufficient = (value_counts >= settings.min_cohort_size).sum() >= 2
    if not sufficient:
        warnings.append(
            f"Not enough data per group (need >= {settings.min_cohort_size} candidates per "
            f"'{attribute_col}' value) to compute statistically meaningful results. "
            f"This protects both statistical validity and candidate privacy."
        )

    fisher_results = run_fisher_tests(df, attribute_col) if sufficient else []
    logistic_result = run_logistic_regression(df, attribute_col) if sufficient else None

    return BiasAuditResult(
        fisher_tests=fisher_results,
        logistic_summary=logistic_result,
        warnings=warnings,
        sufficient_sample=sufficient,
    )
