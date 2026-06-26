# InvestGuide

AI-powered Zimbabwean investment intelligence platform.

## Stack
- Next.js
- FastAPI
- PostgreSQL
- Redis
- Python
- AI/RAG systems

## Architecture
Modular monolith architecture designed for AI-assisted development.

## Documentation
See /docs for:
- PRD
- architecture
- startup blueprint
- technical planning
- AI-agent rules

## Engineering Principles
- modular architecture
- analytics-first
- explainable AI
- responsive fintech UI
- scalable infrastructure
## Local Backend Development

Use the one-command development launcher from the repository root:

```bash
python backend/scripts/dev.py --port 8001
```

The launcher checks Docker, starts the Compose PostgreSQL service, waits for the database, runs backend bootstrap migrations and seed data, then starts FastAPI with Uvicorn.

Useful flags:

```bash
python backend/scripts/dev.py --no-server
python backend/scripts/dev.py --port 8001
python backend/scripts/dev.py --skip-docker
python backend/scripts/dev.py --skip-bootstrap
```

Manual commands remain available when troubleshooting:

```bash
docker compose up -d
python backend/scripts/bootstrap_dev.py
python backend/scripts/check_database.py
```

Health check:

```bash
curl http://127.0.0.1:8001/api/v1/health
```

The Compose stack runs PostgreSQL 16 with a named volume and development-only credentials from `backend/.env.example`. The launcher does not reset databases, delete volumes, enable WRITE ingestion mode, start schedulers, start scrapers, or run live scraping. Do not commit `.env` or hosted database credentials.

