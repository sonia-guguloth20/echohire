import uuid

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import InterviewRound, Candidate, JobPosting, Feedback
from app.schemas import BiasAuditRequest
from app.services.outcome_bias_stats import run_full_audit
from app.services.embedding_analysis import analyze_feedback_clusters

router = APIRouter(prefix="/bias-analysis", tags=["bias-analysis"])

ALLOWED_ATTRIBUTES = {
    "gender_self_reported",
    "age_bracket_self_reported",
    "race_ethnicity_self_reported",
}


@router.post("/audit")
def run_audit(payload: BiasAuditRequest, db: Session = Depends(get_db)):
    if payload.attribute not in ALLOWED_ATTRIBUTES:
        raise HTTPException(status_code=400, detail=f"attribute must be one of {ALLOWED_ATTRIBUTES}")

    jp = db.query(JobPosting).get(payload.job_posting_id)
    if not jp:
        raise HTTPException(status_code=404, detail="Job posting not found")

    rows = (
        db.query(
            InterviewRound.outcome,
            InterviewRound.round_number,
            JobPosting.department,
            getattr(Candidate, payload.attribute).label("attribute_value"),
            InterviewRound.id.label("round_id"),
        )
        .join(Candidate, Candidate.id == InterviewRound.candidate_id)
        .join(JobPosting, JobPosting.id == InterviewRound.job_posting_id)
        .filter(InterviewRound.job_posting_id == payload.job_posting_id)
        .all()
    )

    if not rows:
        raise HTTPException(status_code=404, detail="No interview data found for this job posting")

    df = pd.DataFrame(
        [
            {
                "outcome": r.outcome.value if hasattr(r.outcome, "value") else r.outcome,
                "round_number": r.round_number,
                "department": r.department,
                "attribute_value": r.attribute_value,
                "round_id": r.round_id,
            }
            for r in rows
        ]
    )
    df = df.rename(columns={"attribute_value": payload.attribute})

    stats_result = run_full_audit(df, payload.attribute)

    response = {
        "job_posting_id": str(payload.job_posting_id),
        "attribute_analyzed": payload.attribute,
        "sufficient_sample": stats_result.sufficient_sample,
        "warnings": stats_result.warnings,
        "fisher_exact_tests": [f.__dict__ for f in stats_result.fisher_tests],
        "logistic_regression": stats_result.logistic_summary.__dict__ if stats_result.logistic_summary else None,
    }

    if payload.include_embedding_analysis and stats_result.sufficient_sample:
        feedback_rows = (
            db.query(Feedback.raw_text, InterviewRound.outcome, getattr(Candidate, payload.attribute))
            .join(InterviewRound, InterviewRound.id == Feedback.interview_round_id)
            .join(Candidate, Candidate.id == InterviewRound.candidate_id)
            .filter(InterviewRound.job_posting_id == payload.job_posting_id)
            .all()
        )
        if feedback_rows:
            texts = [r[0] for r in feedback_rows]
            outcomes = [r[1].value if hasattr(r[1], "value") else r[1] for r in feedback_rows]
            attrs = [str(r[2]) for r in feedback_rows]
            response["embedding_cluster_analysis"] = analyze_feedback_clusters(texts, outcomes, attrs)

    return response
