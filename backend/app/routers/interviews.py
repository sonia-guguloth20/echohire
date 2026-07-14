from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import InterviewRound, Feedback
from app.schemas import InterviewRoundCreate

router = APIRouter(prefix="/interviews", tags=["interviews"])


@router.post("/")
def create_interview_round(payload: InterviewRoundCreate, db: Session = Depends(get_db)):
    round_ = InterviewRound(
        candidate_id=payload.candidate_id,
        job_posting_id=payload.job_posting_id,
        interviewer_id=payload.interviewer_id,
        round_number=payload.round_number,
        outcome=payload.outcome,
    )
    db.add(round_)
    db.flush()  # get round_.id before commit

    if payload.feedback_text:
        fb = Feedback(interview_round_id=round_.id, raw_text=payload.feedback_text)
        db.add(fb)

    db.commit()
    db.refresh(round_)
    return {"id": round_.id, "outcome": round_.outcome}


# NOTE: for bulk CSV upload (mentioned in the README roadmap), add a
# POST /interviews/bulk-upload endpoint here that accepts an UploadFile,
# parses it with pandas.read_csv, and loops the rows through the same
# logic as create_interview_round above. Left as a next step since it
# depends on your exact CSV column format.
