from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict
from backend.api.config import settings

router = APIRouter(prefix="/api/v1/scrapers", tags=["scrapers"])

# In-memory registry placeholder
JOB_REGISTRY: Dict[str, Dict] = {
    "federal:*:daily": {"enabled": True, "last_run": None},
    "provincial:on:*:daily": {"enabled": True, "last_run": None},
}

class RunNowRequest(BaseModel):
    scope: str

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
    return {"id": body.job_id, **JOB_REGISTRY[body.job_id]}

# POST run-now (placeholder)
@router.post("/run-now")
def run_now(body: RunNowRequest):
    if not getattr(settings, "scraper_service_enabled", False):
        raise HTTPException(status_code=503, detail="Scraper service disabled")
    # trigger CLI async (real impl: queue or subprocess)
    return {"status": "queued", "scope": body.scope}