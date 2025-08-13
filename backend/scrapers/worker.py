import os
import json
import time
import logging
from typing import Dict, Any, List

import redis
import requests
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import FastAPI
from sqlalchemy import create_engine, text

from .federal_parliament_scraper import FederalParliamentScraper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("scrapers.worker")

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
QUEUE_KEY = os.getenv("SCRAPER_QUEUE_KEY", "scraper_jobs")
POLL_INTERVAL = float(os.getenv("POLL_INTERVAL", "2.0"))
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "1"))
API_BASE = os.getenv("API_BASE", "http://api:8000")
DATABASE_URL_MAIN = os.getenv("DATABASE_URL_MAIN", os.getenv("DATABASE_URL", "postgresql+psycopg://openpolicy:openpolicy123@postgres:5432/openpolicy"))
DATABASE_URL_TEST = os.getenv("DATABASE_URL_TEST", "postgresql+psycopg://openpolicy:openpolicy123@postgres:5432/openpolicy_test")
MCP_ENABLED = os.getenv("MCP_ENABLED", "true").lower() == "true"
MCP_ALLOW_INVALID = os.getenv("MCP_ALLOW_INVALID", "false").lower() == "true"

JOBS_CONSUMED = Counter("scraper_jobs_consumed_total", "Jobs consumed", ["scraper"])
TASKS_COMPLETED = Counter("scraper_tasks_completed_total", "Tasks completed", ["scraper", "task"])
TASKS_FAILED = Counter("scraper_tasks_failed_total", "Tasks failed", ["scraper", "task"])
RUN_DURATION = Histogram("scraper_run_seconds", "Duration of a job run in seconds", ["scraper"])
LAST_RUN_TS = Gauge("scraper_last_run_timestamp", "Unix ts of last successful run", ["scraper"]) 

app = FastAPI(title="Scrapers Worker")
engine_main = create_engine(DATABASE_URL_MAIN, pool_pre_ping=True, future=True)
engine_test = create_engine(DATABASE_URL_TEST, pool_pre_ping=True, future=True)

@app.get("/metrics")
async def metrics():
    return app.response_class(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/health")
async def health():
    return {"status": "ok", "time": time.time()}


def _select_engine(mode: str):
    if (mode or "prod").lower() == "test":
        return engine_test
    return engine_main


def upsert_bills(engine, bills: List[Dict[str, Any]]):
    if not bills:
        return
    with engine.begin() as conn:
        conn.execute(text(
            """
            CREATE TABLE IF NOT EXISTS federal_bills (
              id SERIAL PRIMARY KEY,
              bill_number TEXT,
              title TEXT,
              description TEXT,
              introduced_date DATE,
              sponsor TEXT,
              jurisdiction TEXT,
              status TEXT,
              scraped_at TIMESTAMP,
              UNIQUE (bill_number, title)
            )
            """
        ))
        for b in bills:
            conn.execute(text(
                """
                INSERT INTO federal_bills (bill_number, title, description, introduced_date, sponsor, jurisdiction, status, scraped_at)
                VALUES (:bill_number, :title, :description, :introduced_date, :sponsor, :jurisdiction, :status, :scraped_at)
                ON CONFLICT (bill_number, title) DO UPDATE SET
                  description = EXCLUDED.description,
                  introduced_date = EXCLUDED.introduced_date,
                  sponsor = EXCLUDED.sponsor,
                  status = EXCLUDED.status,
                  scraped_at = EXCLUDED.scraped_at
                """
            ), b)


def upsert_mps(engine, mps: List[Dict[str, Any]]):
    if not mps:
        return
    with engine.begin() as conn:
        conn.execute(text(
            """
            CREATE TABLE IF NOT EXISTS federal_mps (
              id SERIAL PRIMARY KEY,
              name TEXT,
              party TEXT,
              constituency TEXT,
              email TEXT,
              phone TEXT,
              jurisdiction TEXT,
              scraped_at TIMESTAMP,
              UNIQUE (name, constituency)
            )
            """
        ))
    
        for mp in mps:
            conn.execute(text(
                """
                INSERT INTO federal_mps (name, party, constituency, email, phone, jurisdiction, scraped_at)
                VALUES (:name, :party, :constituency, :email, :phone, :jurisdiction, :scraped_at)
                ON CONFLICT (name, constituency) DO UPDATE SET
                  party = EXCLUDED.party,
                  email = EXCLUDED.email,
                  phone = EXCLUDED.phone,
                  scraped_at = EXCLUDED.scraped_at
                """
            ), mp)


def upsert_votes(engine, votes: List[Dict[str, Any]]):
    if not votes:
        return
    with engine.begin() as conn:
        conn.execute(text(
            """
            CREATE TABLE IF NOT EXISTS federal_votes (
              id SERIAL PRIMARY KEY,
              bill_number TEXT,
              vote_date DATE,
              vote_type TEXT,
              result TEXT,
              yea_votes INT,
              nay_votes INT,
              abstentions INT,
              jurisdiction TEXT,
              scraped_at TIMESTAMP,
              UNIQUE (bill_number, vote_date)
            )
            """
        ))
        for v in votes:
            conn.execute(text(
                """
                INSERT INTO federal_votes (bill_number, vote_date, vote_type, result, yea_votes, nay_votes, abstentions, jurisdiction, scraped_at)
                VALUES (:bill_number, :vote_date, :vote_type, :result, :yea_votes, :nay_votes, :abstentions, :jurisdiction, :scraped_at)
                ON CONFLICT (bill_number, vote_date) DO UPDATE SET
                  vote_type = EXCLUDED.vote_type,
                  result = EXCLUDED.result,
                  yea_votes = EXCLUDED.yea_votes,
                  nay_votes = EXCLUDED.nay_votes,
                  abstentions = EXCLUDED.abstentions,
                  scraped_at = EXCLUDED.scraped_at
                """
            ), v)


def process_federal(mode: str, tasks: List[str]):
    scraper = FederalParliamentScraper()
    engine = _select_engine(mode)

    def mcp_validate(data: Dict[str, List[Dict[str, Any]]]) -> bool:
        if not MCP_ENABLED:
            return True
        is_valid = scraper.validate_data(data)
        if not is_valid and not MCP_ALLOW_INVALID:
            logger.warning("MCP validation failed (mode=%s)", mode)
        return is_valid or MCP_ALLOW_INVALID

    if "bills" in tasks:
        try:
            bills = scraper.scrape_bills()
            if mcp_validate({"bills": bills, "mps": [], "votes": []}):
                upsert_bills(engine, bills)
            TASKS_COMPLETED.labels(scraper="federal_parliament", task="bills").inc(len(bills))
        except Exception:
            logger.exception("bills task failed")
            TASKS_FAILED.labels(scraper="federal_parliament", task="bills").inc()
    if "mps" in tasks:
        try:
            mps = scraper.scrape_mps()
            if mcp_validate({"bills": [], "mps": mps, "votes": []}):
                upsert_mps(engine, mps)
            TASKS_COMPLETED.labels(scraper="federal_parliament", task="mps").inc(len(mps))
        except Exception:
            logger.exception("mps task failed")
            TASKS_FAILED.labels(scraper="federal_parliament", task="mps").inc()
    if "votes" in tasks:
        try:
            votes = scraper.scrape_votes()
            if mcp_validate({"bills": [], "mps": [], "votes": votes}):
                upsert_votes(engine, votes)
            TASKS_COMPLETED.labels(scraper="federal_parliament", task="votes").inc(len(votes))
        except Exception:
            logger.exception("votes task failed")
            TASKS_FAILED.labels(scraper="federal_parliament", task="votes").inc()


def run_loop():
    r = redis.from_url(REDIS_URL)
    while True:
        item = r.brpop(QUEUE_KEY, timeout=int(POLL_INTERVAL))
        if not item:
            continue
        _, payload_bytes = item
        try:
            payload = json.loads(payload_bytes.decode("utf-8"))
        except Exception:
            logger.warning("Invalid payload: %s", payload_bytes[:200])
            continue
        scraper = payload.get("scraper")
        tasks = payload.get("tasks", [])
        mode = payload.get("mode", "prod")
        start = time.time()
        try:
            if scraper == "federal_parliament":
                process_federal(mode, tasks)
                JOBS_CONSUMED.labels(scraper="federal_parliament").inc()
                LAST_RUN_TS.labels(scraper="federal_parliament").set(time.time())
        except Exception as e:
            logger.exception("Worker error: %s", e)
        finally:
            RUN_DURATION.labels(scraper=scraper or "unknown").observe(time.time() - start)


@app.on_event("startup")
def on_startup():
    import threading
    t = threading.Thread(target=run_loop, daemon=True)
    t.start()
    logger.info("Worker started")


@app.on_event("shutdown")
def on_shutdown():
    logger.info("Worker stopped")