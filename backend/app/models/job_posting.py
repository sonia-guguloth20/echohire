import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Float, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.database import Base


class JobPosting(Base):
    """
    A single version of a JD. Editing a JD creates a NEW row with the same
    `lineage_id` and an incremented `jd_version`, so bias score history is
    preserved and you can prove "we improved after the audit."
    """
    __tablename__ = "job_postings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)

    # groups together every version of "the same" JD
    lineage_id = Column(UUID(as_uuid=True), default=uuid.uuid4, nullable=False)
    jd_version = Column(Integer, default=1, nullable=False)

    title = Column(String, nullable=False)
    department = Column(String, nullable=True)
    jd_text = Column(Text, nullable=False)

    bias_score = Column(Float, nullable=True)           # 0 (clean) - 100 (heavily biased)
    flagged_phrases = Column(JSONB, nullable=True)       # [{"phrase": "...", "category": "masculine-coded", "suggestion": "..."}]

    created_at = Column(DateTime, default=datetime.utcnow)

    company = relationship("Company", back_populates="job_postings")
    interview_rounds = relationship("InterviewRound", back_populates="job_posting")
