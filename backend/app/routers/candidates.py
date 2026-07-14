from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Candidate
from app.schemas import CandidateCreate

router = APIRouter(prefix="/candidates", tags=["candidates"])


@router.post("/")
def create_candidate(payload: CandidateCreate, db: Session = Depends(get_db)):
    candidate = Candidate(**payload.model_dump())
    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    # Never echo protected attributes back in the response body -
    # they were provided by the client so this isn't a leak, but it's a
    # good habit to keep this endpoint's response minimal.
    return {"id": candidate.id, "external_ref": candidate.external_ref}
