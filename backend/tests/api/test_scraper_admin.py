import os
import importlib
import pytest
from fastapi.testclient import TestClient

# Ensure settings pick up env flag (set before app import)
os.environ["SCRAPER_SERVICE_ENABLED"] = "true"

from backend.api.main import app

client = TestClient(app)

def test_status_endpoint():
    r = client.get("/api/v1/scrapers/service-status")
    assert r.status_code == 200
    assert isinstance(r.json().get("enabled"), bool)


def test_jobs_list_and_toggle_and_run_now(auth_headers):
    # enable flag first
    client.post("/api/v1/admin/config/scraper/feature-flag", json={"enabled": True}, headers=auth_headers)
    # list
    r = client.get("/api/v1/scrapers/jobs")
    assert r.status_code == 200
    jobs = r.json()
    assert isinstance(jobs, list)
    assert any("id" in j for j in jobs)
    # toggle
    job_id = jobs[0]["id"]
    r = client.post("/api/v1/scrapers/jobs/toggle", json={"job_id": job_id, "enabled": True})
    assert r.status_code == 200
    # run-now
    r = client.post("/api/v1/scrapers/run-now", json={"scope": "federal:*", "mode": "daily"})
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "queued"
    assert body["scope"] == "federal:*"


def test_get_scraper_config_and_toggle_flag(auth_headers):
    r = client.get("/api/v1/admin/config/scraper", headers=auth_headers)
    assert r.status_code == 200
    cfg = r.json()
    assert "scraper_service_enabled" in cfg
    # toggle
    prev = cfg["scraper_service_enabled"]
    r = client.post("/api/v1/admin/config/scraper/feature-flag", json={"enabled": not prev}, headers=auth_headers)
    assert r.status_code == 200
    r2 = client.get("/api/v1/admin/config/scraper", headers=auth_headers)
    assert r2.json()["scraper_service_enabled"] == (not prev)


def test_run_all_daily_and_unified_status(auth_headers):
    # Ensure feature flag on
    client.post("/api/v1/admin/config/scraper/feature-flag", json={"enabled": True}, headers=auth_headers)
    # Run all
    r = client.post("/api/v1/scrapers/run-now", json={"scope": "*:*", "mode": "daily"})
    assert r.status_code == 200
    # Unified status
    r2 = client.get("/api/v1/admin/status/unified", headers=auth_headers)
    assert r2.status_code == 200
    body = r2.json()
    assert "api" in body and "scraper_service" in body


def test_effective_config_endpoint(auth_headers):
    r = client.get("/api/v1/admin/config/effective", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert "host" in data and "port" in data and "environment" in data