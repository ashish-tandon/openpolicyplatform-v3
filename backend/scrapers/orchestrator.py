import os
import json
import time
import logging
from datetime import datetime
from typing import Dict, Any

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI
from prometheus_client import Counter, Gauge, generate_latest, CONTENT_TYPE_LATEST
import redis

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("scrapers.orchestrator")

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
QUEUE_KEY = os.getenv("SCRAPER_QUEUE_KEY", "scraper_jobs")

app = FastAPI(title="Scrapers Orchestrator")

JOBS_ENQUEUED = Counter("scraper_jobs_enqueued_total", "Jobs enqueued", ["scraper"])
LAST_ENQUEUE_TS = Gauge("scraper_last_enqueue_timestamp", "Unix ts of last enqueue", ["scraper"])

redis_client = redis.from_url(REDIS_URL)
scheduler = BackgroundScheduler(timezone="UTC")


def enqueue_job(payload: Dict[str, Any]):
    redis_client.lpush(QUEUE_KEY, json.dumps(payload))


@app.get("/metrics")
async def metrics():
    return app.response_class(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/health")
async def health():
    return {"status": "ok", "time": datetime.utcnow().isoformat()}


def enqueue_federal(mode: str):
    payload = {
        "scraper": "federal_parliament",
        "mode": mode,
        "tasks": ["bills", "mps", "votes"],
        "enqueued_at": time.time(),
    }
    enqueue_job(payload)
    JOBS_ENQUEUED.labels(scraper="federal_parliament").inc()
    LAST_ENQUEUE_TS.labels(scraper="federal_parliament").set(time.time())
    logger.info("Enqueued federal_parliament job (mode=%s)", mode)


@app.on_event("startup")
def on_startup():
    # Default prod schedule: every day at 02:00 UTC
    prod_cron = os.getenv("FEDERAL_PROD_SCHEDULE_CRON", "0 2 * * *")
    test_cron = os.getenv("FEDERAL_TEST_SCHEDULE_CRON", "0 * * * *")  # default hourly for test
    # APScheduler cron: minute hour day month day_of_week
    pm, ph, pdom, pmon, pdow = prod_cron.split()
    tm, th, tdom, tmon, tdow = test_cron.split()

    scheduler.add_job(lambda: enqueue_federal("prod"), "cron", minute=pm, hour=ph, day=pdom, month=pmon, day_of_week=pdow, id="federal_prod", replace_existing=True)
    scheduler.add_job(lambda: enqueue_federal("test"), "cron", minute=tm, hour=th, day=tdom, month=tmon, day_of_week=tdow, id="federal_test", replace_existing=True)

    scheduler.start()
    logger.info("Orchestrator started with prod=%s, test=%s", prod_cron, test_cron)


@app.on_event("shutdown")
def on_shutdown():
    scheduler.shutdown(wait=False)
    logger.info("Orchestrator stopped")