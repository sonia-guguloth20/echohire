# EchoHire

Detect hiring bias in job descriptions and interview outcomes.

## What this repo contains (Phase 1 scaffold)

- FastAPI backend with full schema (companies → job_postings → candidates → interview_rounds → feedback)
- JD language bias scorer (word-list based, upgradeable to a fine-tuned classifier)
- Outcome bias statistics engine (Fisher's Exact Test + logistic regression)
- Feedback embedding clustering (detects semantic drift between accepted/rejected feedback)
- Alembic migrations
- Docker Compose for local dev (Postgres + API)

## Project layout

```
echohire/
├── docker-compose.yml
├── .env.example
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── alembic.ini
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/          <- migration files land here
│   └── app/
│       ├── main.py            <- FastAPI app entrypoint
│       ├── config.py          <- env-based settings
│       ├── database.py        <- SQLAlchemy engine/session
│       ├── models/            <- SQLAlchemy ORM models (the schema)
│       ├── schemas/           <- Pydantic request/response models
│       ├── routers/           <- API endpoints
│       ├── services/          <- the actual bias-detection logic
│       └── data/              <- bias word lists / reference data
```

## Step-by-step setup

1. `cp .env.example .env` and fill in a `DATABASE_URL` / `SECRET_KEY`
2. `docker compose up -d db` — starts Postgres only
3. `cd backend && pip install -r requirements.txt` (use a venv)
4. `alembic upgrade head` — creates all tables
5. `uvicorn app.main:app --reload` — API now live at http://localhost:8000/docs
6. Hit `/companies`, create a company, then `/job-postings` to submit a JD and get a bias score back
7. Use `/interviews/bulk-upload` to load a CSV of interview outcomes, then `/bias-analysis/{job_posting_id}` to run the statistical audit

## Roadmap after this scaffold

- [ ] Swap the word-list JD scorer for a fine-tuned HuggingFace classifier (I can help set up the training pipeline — you'd need a labeled dataset, e.g. the Gaucher/Friesen/Kay word lists as a starting seed)
- [ ] Add `sentence-transformers` embedding job for feedback text (queue via Celery/RQ so it doesn't block requests)
- [ ] PDF report generation (WeasyPrint) + S3 upload
- [ ] Auth (JWT) + multi-tenant scoping so Company A can't see Company B's data
- [ ] Frontend dashboard (React) — window functions already computed server-side, just needs charts
- [ ] Terraform for AWS (RDS + ECS Fargate + S3) — given your background this might be the fastest part for you

I've built the backend scaffold first since that's where the real technical depth (stats + NLP) lives. Say the word and I'll build out the JD analyzer logic, the stats engine, or the Terraform next — happy to go deep on any one piece.
