from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Optional
from backend.api.config import settings
import sys, subprocess
from datetime import datetime
import json as _json
from pathlib import Path
from collections import deque
from time import time as _now

router = APIRouter(prefix="/api/v1/scrapers", tags=["scrapers"])

# In-memory registry placeholder
JOB_REGISTRY: Dict[str, Dict] = {
    "federal:*:daily": {"enabled": True, "last_run": None},
    "provincial:on:*:daily": {"enabled": True, "last_run": None},
}

AUDIT_LOG_PATH = Path(__file__).resolve().parent.parent.parent / "logs" / "admin_audit.log"
AUDIT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

_RATE_BUCKET_RUN: deque = deque()
_RATE_BUCKET_TOGGLE: deque = deque()
_RATE_LIMIT = 10  # events per minute

def _rate_ok(bucket: deque) -> bool:
    now = _now()
    window = 60.0
    # drop older than 60s
    while bucket and now - bucket[0] > window:
        bucket.popleft()
    if len(bucket) >= _RATE_LIMIT:
        return False
    bucket.append(now)
    return True

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

@router.get("/service-status")
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
    if not _rate_ok(_RATE_BUCKET_TOGGLE):
        raise HTTPException(status_code=429, detail="Too many toggle requests")
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
    if not _rate_ok(_RATE_BUCKET_RUN):
        raise HTTPException(status_code=429, detail="Too many run requests")
    background_tasks.add_task(_run_cli_async, body.mode, body.scope, body.since)
    # Record last_run best-effort
    key = f"{body.scope}:{body.mode}" if ":" not in body.scope.split(":")[-1] else body.scope
    JOB_REGISTRY.setdefault(key, {"enabled": True, "last_run": None})
    JOB_REGISTRY[key]["last_run"] = datetime.utcnow().isoformat()
    _audit({"action": "scraper.run_now", "mode": body.mode, "scope": body.scope, "since": body.since})
    return {"status": "queued", "scope": body.scope, "mode": body.mode, "since": body.since}