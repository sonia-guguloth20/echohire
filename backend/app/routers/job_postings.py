import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import JobPosting
from app.schemas import JobPostingCreate, JobPostingOut
from app.services.jd_language_analyzer import score_job_description

router = APIRouter(prefix="/job-postings", tags=["job-postings"])


@router.post("/", response_model=JobPostingOut)
def create_job_posting(payload: JobPostingCreate, db: Session = Depends(get_db)):
    analysis = score_job_description(payload.jd_text)

    lineage_id = payload.lineage_id or uuid.uuid4()
    version = 1
    if payload.lineage_id:
        last_version = (
            db.query(func.max(JobPosting.jd_version))
            .filter(JobPosting.lineage_id == payload.lineage_id)
            .scalar()
        )
        version = (last_version or 0) + 1

    jp = JobPosting(
        company_id=payload.company_id,
        lineage_id=lineage_id,
        jd_version=version,
        title=payload.title,
        department=payload.department,
        jd_text=payload.jd_text,
        bias_score=analysis.bias_score,
        flagged_phrases=analysis.flagged_phrases,
    )
    db.add(jp)
    db.commit()
    db.refresh(jp)
    return jp


@router.get("/{lineage_id}/history", response_model=list[JobPostingOut])
def jd_version_history(lineage_id: uuid.UUID, db: Session = Depends(get_db)):
    """See how the bias score changed across edits of the same JD."""
    versions = (
        db.query(JobPosting)
        .filter(JobPosting.lineage_id == lineage_id)
        .order_by(JobPosting.jd_version.asc())
        .all()
    )
    if not versions:
        raise HTTPException(status_code=404, detail="No job posting found with that lineage_id")
    return versions


@router.get("/{job_posting_id}", response_model=JobPostingOut)
def get_job_posting(job_posting_id: uuid.UUID, db: Session = Depends(get_db)):
    jp = db.query(JobPosting).get(job_posting_id)
    if not jp:
        raise HTTPException(status_code=404, detail="Job posting not found")
    return jp
