#!/usr/bin/env python3
import os
import sys
import requests
import yaml

CENTRAL_CONFIG_PATH = os.getenv("CENTRAL_CONFIG_PATH", os.path.join(os.getcwd(), "config/central-config.yaml"))
API_BASE = os.getenv("API_BASE", "http://localhost:9001")


def load_yaml(path: str):
    with open(path, 'r') as f:
        return yaml.safe_load(f) or {}


def assert_equal(name: str, a, b):
    if a != b:
        print(f"[ERROR] {name} mismatch: expected {a}, got {b}")
        sys.exit(1)


def get(path: str):
    try:
        r = requests.get(API_BASE + path, timeout=10)
    except Exception as e:
        print(f"[ERROR] GET {path} -> exception: {e}")
        sys.exit(1)
    if r.status_code != 200:
        print(f"[ERROR] GET {path} -> {r.status_code}")
        sys.exit(1)
    return r.json()


def try_get(path: str):
    try:
        r = requests.get(API_BASE + path, timeout=10)
        return r
    except Exception:
        return None


def main():
    cfg = load_yaml(CENTRAL_CONFIG_PATH)
    svc = (cfg.get('services') or {}).get('api', {})
    print("[info] central config api:", svc)
    # Check API health endpoints
    _ = get("/api/v1/health")
    _ = get("/api/v1/health/detailed")
    # Effective config via admin (optional; may require auth)
    resp = try_get("/api/v1/admin/config/effective")
    if resp is not None and resp.status_code == 200:
        eff = resp.json()
        exp_host = svc.get('host') or "0.0.0.0"
        exp_port = int(svc.get('port') or 9001)
        assert_equal("host", eff.get('host'), exp_host)
        assert_equal("port", int(eff.get('port')), exp_port)
        print("[info] effective config matches central-config")
    else:
        print("[warn] skipping effective config audit (endpoint not accessible without auth)")
    print("[ok] pre-deploy validation passed")


if __name__ == '__main__':
    main()