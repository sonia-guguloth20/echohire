from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import companies, job_postings, candidates, interviews, bias_analysis

app = FastAPI(
    title="EchoHire API",
    description="Detect hiring bias in job descriptions and interview outcomes.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this before production
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(companies.router)
app.include_router(job_postings.router)
app.include_router(candidates.router)
app.include_router(interviews.router)
app.include_router(bias_analysis.router)


@app.get("/health")
def health():
    return {"status": "ok"}
