from fastapi import APIRouter
from pydantic import BaseModel
router = APIRouter(prefix="/api/v1/scrapers", tags=["scrapers"])

class RunNowRequest(BaseModel):
    scope: str

# GET list of jobs (placeholder)
@router.get("/jobs")
def list_jobs():
    return [
        {"id":"federal:*:daily","enabled":True,"last_run":None},
        {"id":"provincial:on:*:daily","enabled":True,"last_run":None},
    ]

# POST run-now (placeholder)
@router.post("/run-now")
def run_now(body: RunNowRequest):
    # trigger CLI async (real impl: queue or subprocess)
    return {"status":"queued","scope":body.scope}