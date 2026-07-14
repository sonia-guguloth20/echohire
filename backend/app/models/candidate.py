import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class Candidate(Base):
    """
    Protected attributes here are OPTIONAL and self-disclosed by the candidate
    during application (standard EEOC-style voluntary disclosure form) — they
    are never inferred by the platform from a name, photo, or resume.

    These fields are only ever read by the stats engine in aggregate, on
    cohorts >= settings.min_cohort_size. No endpoint should ever return these
    fields on a per-candidate basis to an end user.
    """
    __tablename__ = "candidates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)

    external_ref = Column(String, nullable=True)  # company's own ATS candidate ID, not a real name

    gender_self_reported = Column(String, nullable=True)          # optional, free text or enum
    age_bracket_self_reported = Column(String, nullable=True)     # e.g. "25-34", optional
    race_ethnicity_self_reported = Column(String, nullable=True)  # optional

    created_at = Column(DateTime, default=datetime.utcnow)

    company = relationship("Company", back_populates="candidates")
    interview_rounds = relationship("InterviewRound", back_populates="candidate", cascade="all, delete-orphan")
