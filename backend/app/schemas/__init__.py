import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class CompanyCreate(BaseModel):
    name: str
    industry: Optional[str] = None


class CompanyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    industry: Optional[str]
    created_at: datetime


class JobPostingCreate(BaseModel):
    company_id: uuid.UUID
    title: str
    department: Optional[str] = None
    jd_text: str
    # if editing an existing JD, pass its lineage_id to version it
    lineage_id: Optional[uuid.UUID] = None


class JobPostingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    company_id: uuid.UUID
    lineage_id: uuid.UUID
    jd_version: int
    title: str
    department: Optional[str]
    bias_score: Optional[float]
    flagged_phrases: Optional[list]
    created_at: datetime


class CandidateCreate(BaseModel):
    company_id: uuid.UUID
    external_ref: Optional[str] = None
    gender_self_reported: Optional[str] = None
    age_bracket_self_reported: Optional[str] = None
    race_ethnicity_self_reported: Optional[str] = None


class InterviewRoundCreate(BaseModel):
    candidate_id: uuid.UUID
    job_posting_id: uuid.UUID
    interviewer_id: Optional[uuid.UUID] = None
    round_number: int = 1
    outcome: str  # advanced | rejected | offered | withdrew
    feedback_text: Optional[str] = None


class BiasAuditRequest(BaseModel):
    job_posting_id: uuid.UUID
    attribute: str  # "gender_self_reported" | "age_bracket_self_reported" | "race_ethnicity_self_reported"
    include_embedding_analysis: bool = True
