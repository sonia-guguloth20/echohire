import uuid
import enum
from datetime import datetime

from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class OutcomeEnum(str, enum.Enum):
    advanced = "advanced"
    rejected = "rejected"
    offered = "offered"
    withdrew = "withdrew"


class Interviewer(Base):
    __tablename__ = "interviewers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    name_or_alias = Column(String, nullable=False)  # can be pseudonymized, e.g. "Interviewer_04"

    company = relationship("Company", back_populates="interviewers")
    interview_rounds = relationship("InterviewRound", back_populates="interviewer")


class InterviewRound(Base):
    __tablename__ = "interview_rounds"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id"), nullable=False)
    job_posting_id = Column(UUID(as_uuid=True), ForeignKey("job_postings.id"), nullable=False)
    interviewer_id = Column(UUID(as_uuid=True), ForeignKey("interviewers.id"), nullable=True)

    round_number = Column(Integer, default=1)
    outcome = Column(Enum(OutcomeEnum), nullable=False)
    scheduled_at = Column(DateTime, default=datetime.utcnow)

    candidate = relationship("Candidate", back_populates="interview_rounds")
    job_posting = relationship("JobPosting", back_populates="interview_rounds")
    interviewer = relationship("Interviewer", back_populates="interview_rounds")
    feedback = relationship("Feedback", back_populates="interview_round", uselist=False, cascade="all, delete-orphan")
