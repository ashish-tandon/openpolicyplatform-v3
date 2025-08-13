from fastapi import APIRouter
router = APIRouter(prefix="/api/v1/scrapers", tags=["scrapers"])

# GET list of jobs (placeholder)
@router.get("/jobs")
def list_jobs():
    return [
        {"id":"federal:*:daily","enabled":True,"last_run":None},
        {"id":"provincial:on:*:daily","enabled":True,"last_run":None},
    ]

# POST run-now (placeholder)
@router.post("/run-now")
def run_now(scope: str):
    # trigger CLI async (real impl: queue or subprocess)
    return {"status":"queued","scope":scope}