import os
import importlib
import pytest
from fastapi.testclient import TestClient

# Ensure settings pick up env flag
os.environ["SCRAPER_SERVICE_ENABLED"] = "true"

from backend.api.main import app

client = TestClient(app)

def test_status_endpoint():
    r = client.get("/api/v1/scrapers/status")
    assert r.status_code == 200
    assert isinstance(r.json().get("enabled"), bool)

def test_jobs_list_and_toggle_and_run_now():
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

def test_get_scraper_config_and_toggle_flag():
    r = client.get("/api/v1/admin/config/scraper")
    assert r.status_code == 200
    cfg = r.json()
    assert "scraper_service_enabled" in cfg
    # toggle
    prev = cfg["scraper_service_enabled"]
    r = client.post("/api/v1/admin/config/scraper/feature-flag", json={"enabled": not prev})
    assert r.status_code == 200
    r2 = client.get("/api/v1/admin/config/scraper")
    assert r2.json()["scraper_service_enabled"] == (not prev)