import time
import logging
from typing import Any, Dict, List, Optional

import requests
from sqlalchemy import text
from sqlalchemy.engine import Engine

logger = logging.getLogger("scrapers.adapters")

REPRESENT_BASE = "https://represent.opennorth.ca"


def _get_json(url: str, timeout: int = 20) -> Optional[Dict[str, Any]]:
    try:
        resp = requests.get(url, timeout=timeout, headers={"User-Agent": "OpenPolicyBot/1.0"})
        resp.raise_for_status()
        return resp.json()
    except Exception as exc:
        logger.warning("represent API request failed: %s -> %s", url, exc)
        return None


def fetch_represent_jurisdictions(limit: int = 200) -> List[Dict[str, Any]]:
    url = f"{REPRESENT_BASE}/jurisdictions/?limit={limit}"
    data = _get_json(url)
    results: List[Dict[str, Any]] = []
    if not data:
        return results
    for item in data.get("objects", data.get("results", [])):
        results.append({
            "slug": item.get("slug") or item.get("id"),
            "name": item.get("name"),
            "level": item.get("level"),
            "province": item.get("province") or item.get("province_code"),
            "source_url": url,
            "scraped_at": int(time.time()),
        })
    return results


def upsert_represent_jurisdictions(engine: Engine, jurisdictions: List[Dict[str, Any]]) -> None:
    if not jurisdictions:
        return
    with engine.begin() as conn:
        conn.execute(text(
            """
            CREATE TABLE IF NOT EXISTS reference_jurisdictions (
              id SERIAL PRIMARY KEY,
              slug TEXT UNIQUE,
              name TEXT,
              level TEXT,
              province TEXT,
              source_url TEXT,
              scraped_at BIGINT
            )
            """
        ))
        for j in jurisdictions:
            conn.execute(text(
                """
                INSERT INTO reference_jurisdictions (slug, name, level, province, source_url, scraped_at)
                VALUES (:slug, :name, :level, :province, :source_url, :scraped_at)
                ON CONFLICT (slug) DO UPDATE SET
                  name = EXCLUDED.name,
                  level = EXCLUDED.level,
                  province = EXCLUDED.province,
                  source_url = EXCLUDED.source_url,
                  scraped_at = EXCLUDED.scraped_at
                """
            ), j)


def fetch_represent_districts(boundary_set: str = "electoral-districts", limit: int = 200) -> List[Dict[str, Any]]:
    url = f"{REPRESENT_BASE}/boundaries/{boundary_set}/?limit={limit}"
    data = _get_json(url)
    results: List[Dict[str, Any]] = []
    if not data:
        return results
    for item in data.get("objects", data.get("results", [])):
        results.append({
            "external_id": item.get("external_id") or item.get("id"),
            "name": item.get("name"),
            "boundary_set": boundary_set,
            "source_url": url,
            "scraped_at": int(time.time()),
        })
    return results


def upsert_represent_districts(engine: Engine, districts: List[Dict[str, Any]]) -> None:
    if not districts:
        return
    with engine.begin() as conn:
        conn.execute(text(
            """
            CREATE TABLE IF NOT EXISTS reference_districts (
              id SERIAL PRIMARY KEY,
              external_id TEXT,
              name TEXT,
              boundary_set TEXT,
              source_url TEXT,
              scraped_at BIGINT,
              UNIQUE (boundary_set, name)
            )
            """
        ))
        for d in districts:
            conn.execute(text(
                """
                INSERT INTO reference_districts (external_id, name, boundary_set, source_url, scraped_at)
                VALUES (:external_id, :name, :boundary_set, :source_url, :scraped_at)
                ON CONFLICT (boundary_set, name) DO UPDATE SET
                  external_id = EXCLUDED.external_id,
                  source_url = EXCLUDED.source_url,
                  scraped_at = EXCLUDED.scraped_at
                """
            ), d)