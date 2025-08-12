# Architecture Diagram

```
                 ┌────────────────────────────────────────────────┐
                 │                    Users                       │
                 │     (Public, Admin, Integrations)              │
                 └────────────────────────────────────────────────┘
                                      │
                                      ▼
                        ┌───────────────────────────┐
                        │      Frontend (Web)       │
                        │  React + Vite (5173)      │
                        │  Env: VITE_API_URL        │
                        └──────────────┬────────────┘
                                       │ REST
                                       │
                                       ▼
                 ┌────────────────────────────────────────────────┐
                 │              Backend API (FastAPI)             │
                 │   Uvicorn (8000)  |  /api/v1/*                 │
                 │   Security, Rate Limiting, Caching             │
                 │   Env via Settings (backend/api/config.py)     │
                 └──────────────┬─────────────────────────────────┘
                                │
                  ┌─────────────┴─────────────┐
                  │                           │
                  ▼                           ▼
      ┌───────────────────────┐     ┌──────────────────────────┐
      │ PostgreSQL Database   │     │   Reports/Logs Storage   │
      │ (core_politician,     │     │  scraper_test_report_*.  │
      │  bills_bill, …)       │     │  collection_report_*.    │
      └──────────┬────────────┘     └──────────────┬───────────┘
                 │                                  │
                 │                                  │
                 ▼                                  ▼
        ┌────────────────┐                 ┌─────────────────────┐
        │   Scrapers     │──────────────▶  │  Report Generation  │
        │ (various)      │                 │  + Logs             │
        └────────────────┘                 └─────────────────────┘

Legend:
- Frontend uses Backend via REST
- Backend reads DB for data endpoints and reports/logs for monitoring endpoints
- Env variables defined in .env propagate to Settings and Vite