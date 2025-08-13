# 🏛️ Open Policy Platform

A unified platform for policy analysis, data collection, and public access to parliamentary information.

## 🎯 **Overview**

The Open Policy Platform is a comprehensive system that merges multiple specialized repositories into a unified codebase for managing, analyzing, and presenting policy data. It provides both public access to policy information and administrative tools for data management.

## 🏗️ **Architecture**

### **Unified Backend Service** (`backend/`)
- **FastAPI Application**: RESTful API with automatic documentation
- **PostgreSQL Database**: 6.5GB of parliamentary data
- **Integrated Scrapers**: Automated data collection pipeline
- **Admin API**: Built-in administrative functions
- **Authentication**: JWT-based role management

### **Unified Web Application** (`web/`)
- **React + TypeScript**: Modern web interface
- **Role-Based Access**: Public and admin interfaces
- **Responsive Design**: Works on all devices
- **Real-Time Updates**: Live data synchronization
- **Admin Dashboard**: Complete system management

## 📦 Services

- `postgres`: PostgreSQL database (plus `openpolicy_test` for scraper test mode)
- `api`: FastAPI backend
- `web`: React web app
- `redis`: Queue for scraper jobs
- `scrapers-orchestrator`: Schedules and enqueues scraper jobs
- `scrapers-worker`: Consumes jobs, runs scrapers, persists data
- `headless-browser`: Browserless Chrome for JS-heavy scraping (optional)
- `prometheus`: Metrics scraping
- `grafana`: Dashboards

## 🗄️ Dual Databases for Scrapers

- Production DB: `openpolicy`
- Test DB: `openpolicy_test` (auto-created via `docker/postgres-init/01-init.sql`)
- Orchestrator enqueues jobs with `mode` = `prod` or `test`.
- Worker routes persistence to the correct DB by mode.

## ⏰ Scraper Scheduling

- Registry: `backend/scrapers/registry.py`
- Enable per mode via env on orchestrator:
  - `ENABLED_SCRAPERS_PROD=federal_parliament`
  - `ENABLED_SCRAPERS_TEST=federal_parliament,represent_opennorth_ref`
- Per-scraper cron override envs (optional):
  - `FEDERAL_PARLIAMENT_PROD_CRON`, `FEDERAL_PARLIAMENT_TEST_CRON`, etc.

## ✅ Current Scrapers

- `federal_parliament`: bills, mps, votes (persisted with upserts)
- `represent_opennorth_ref`: jurisdictions, districts (persisted with upserts)
- Placeholders in worker for other planned scrapers from `opencivicdata/scrapers-ca` and `openparliament` historic import.

## 🔧 Quick Start

1) Prereqs: Node.js 18+, Python 3.11+, Git
2) Start (Docker recommended when available):
```bash
# API dev (no Docker): in backend venv
python -m pytest tests/api -q
# Compose (when Docker available)
docker compose up -d --build
```

## 🔭 Monitoring

- Prometheus scrapes: `api:8000`, `scrapers-orchestrator:8010`, `scrapers-worker:8011`
- Grafana dashboards can be provisioned from `backend/monitoring/grafana-provisioning`.

## 🧩 External Ingestion

Cloned under `external/` via `scripts/ingest_repos.sh`:
- `michaelmulley/openparliament`
- `rarewox/open-policy-infra`
- `rarewox/admin-open-policy`
- `rarewox/open-policy-app`
- `opencivicdata/scrapers-ca`
- `biglocalnews/civic-scraper`

Note: `rarewox/open-policy-web` repo not found.

## 🧪 Tests

- Backend API tests: `python -m pytest tests/api -q` (35 passing)

---

**🎉 Open Policy Platform - Making Policy Data Accessible to Everyone**

*Last Updated: August 8, 2024*
*Version: 1.0.0*
