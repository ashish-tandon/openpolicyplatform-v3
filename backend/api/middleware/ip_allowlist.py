from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, PlainTextResponse
from ipaddress import ip_network, ip_address
from typing import List
from backend.config.central import get_service_config
from backend.api.config import settings

class IPAllowlistMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, service_name: str = "api"):
        super().__init__(app)
        self.service_name = service_name
        svc = get_service_config(service_name)
        self.allowed_cidrs: List[str] = list(svc.get("allowed_ips") or [])
        # If no allowlist configured, default allow all
        if not self.allowed_cidrs:
            self.allowed_networks = [ip_network("0.0.0.0/0")]
        else:
            self.allowed_networks = [ip_network(c) for c in self.allowed_cidrs]

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else None
        if client_ip:
            ip = ip_address(client_ip)
            if not any(ip in net for net in self.allowed_networks):
                return PlainTextResponse("Forbidden by IP allowlist", status_code=403)
        return await call_next(request)