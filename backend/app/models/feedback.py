import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Text, Float
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship

from app.database import Base


class Feedback(Base):
    """
    Raw interviewer feedback text plus derived fields. `embedding_vector` is
    stored as a plain float array here to avoid requiring the pgvector
    extension for the MVP. If you outgrow this (e.g. want fast nearest-
    neighbor search across thousands of feedback rows), swap this column for
    pgvector's `Vector` type and add an ivfflat index.
    """
    __tablename__ = "feedback"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    interview_round_id = Column(UUID(as_uuid=True), ForeignKey("interview_rounds.id"), nullable=False)

    raw_text = Column(Text, nullable=False)
    sentiment_score = Column(Float, nullable=True)       # -1.0 to 1.0
    embedding_vector = Column(ARRAY(Float), nullable=True)  # 384-dim from all-MiniLM-L6-v2

    created_at = Column(DateTime, default=datetime.utcnow)

    interview_round = relationship("InterviewRound", back_populates="feedback")
