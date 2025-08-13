from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Optional
from backend.api.config import settings
import sys, subprocess
from datetime import datetime
import json as _json
from pathlib import Path

router = APIRouter(prefix="/api/v1/scrapers", tags=["scrapers"])

# In-memory registry placeholder
JOB_REGISTRY: Dict[str, Dict] = {
    "federal:*:daily": {"enabled": True, "last_run": None},
    "provincial:on:*:daily": {"enabled": True, "last_run": None},
}

AUDIT_LOG_PATH = Path(__file__).resolve().parent.parent.parent / "logs" / "admin_audit.log"
AUDIT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

def _audit(event: dict):
    try:
        event_with_ts = {"ts": datetime.utcnow().isoformat(), **event}
        with open(AUDIT_LOG_PATH, "a") as f:
            f.write(_json.dumps(event_with_ts) + "\n")
    except Exception:
        pass

class RunNowRequest(BaseModel):
    scope: str
    mode: str = "daily"  # daily|bootstrap|special
    since: Optional[str] = None  # YYYY-MM-DD

class ToggleJobRequest(BaseModel):
    job_id: str
    enabled: bool

@router.get("/status")
def service_status():
    return {
        "enabled": bool(getattr(settings, "scraper_service_enabled", False)),
    }

# GET list of jobs (placeholder)
@router.get("/jobs")
def list_jobs():
    if not getattr(settings, "scraper_service_enabled", False):
        raise HTTPException(status_code=503, detail="Scraper service disabled")
    return [{"id": k, **v} for k, v in JOB_REGISTRY.items()]

# POST enable/disable a job
@router.post("/jobs/toggle")
def toggle_job(body: ToggleJobRequest):
    if not getattr(settings, "scraper_service_enabled", False):
        raise HTTPException(status_code=503, detail="Scraper service disabled")
    if body.job_id not in JOB_REGISTRY:
        raise HTTPException(status_code=404, detail="Job not found")
    JOB_REGISTRY[body.job_id]["enabled"] = body.enabled
    _audit({"action": "scraper.toggle", "job_id": body.job_id, "enabled": body.enabled})
    return {"id": body.job_id, **JOB_REGISTRY[body.job_id]}

def _run_cli_async(mode: str, scope: str, since: Optional[str] = None):
    cmd = [sys.executable, "-m", "services.scraper.cli", "--mode", mode, "--scope", scope]
    if since:
        cmd += ["--since", since]
    subprocess.Popen(cmd)

# POST run-now (placeholder)
@router.post("/run-now")
def run_now(body: RunNowRequest, background_tasks: BackgroundTasks):
    if not getattr(settings, "scraper_service_enabled", False):
        raise HTTPException(status_code=503, detail="Scraper service disabled")
    background_tasks.add_task(_run_cli_async, body.mode, body.scope, body.since)
    # Record last_run best-effort
    key = f"{body.scope}:{body.mode}" if ":" not in body.scope.split(":")[-1] else body.scope
    JOB_REGISTRY.setdefault(key, {"enabled": True, "last_run": None})
    JOB_REGISTRY[key]["last_run"] = datetime.utcnow().isoformat()
    _audit({"action": "scraper.run_now", "mode": body.mode, "scope": body.scope, "since": body.since})
    return {"status": "queued", "scope": body.scope, "mode": body.mode, "since": body.since}