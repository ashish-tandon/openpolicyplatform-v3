import os
import yaml
from typing import Any, Dict

CENTRAL_CONFIG_PATH = os.getenv("CENTRAL_CONFIG_PATH", os.path.join(os.getcwd(), "config/central-config.yaml"))

def load_central_config() -> Dict[str, Any]:
    try:
        if os.path.exists(CENTRAL_CONFIG_PATH):
            with open(CENTRAL_CONFIG_PATH, 'r') as f:
                return yaml.safe_load(f) or {}
    except Exception:
        pass
    return {}

def get_service_config(service_name: str) -> Dict[str, Any]:
    cfg = load_central_config()
    return (cfg.get('services') or {}).get(service_name, {})

def validate_service_binding(service_name: str, host: str, port: int, environment: str) -> None:
    svc = get_service_config(service_name)
    expected_port = svc.get('port')
    expected_host = svc.get('host')
    if expected_port and int(expected_port) != int(port):
        msg = f"Port mismatch for {service_name}: expected {expected_port}, got {port}"
        if environment.lower() == 'production':
            raise RuntimeError(msg)
        else:
            print(f"[warn] {msg}")
    if expected_host and expected_host != host:
        msg = f"Host mismatch for {service_name}: expected {expected_host}, got {host}"
        if environment.lower() == 'production':
            raise RuntimeError(msg)
        else:
            print(f"[warn] {msg}")