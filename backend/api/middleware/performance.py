"""
Performance Middleware
Provides caching and performance optimizations
"""

import hashlib
import json
import time
from typing import Optional, AsyncIterator
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, StreamingResponse
import logging

logger = logging.getLogger(__name__)

class PerformanceMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, cache_ttl: int = 60, rate_limit_per_minute: int = 60):
        super().__init__(app)
        self.cache_ttl = cache_ttl
        self.cache = {}
        self.timestamps = {}
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        cache_key = self._generate_cache_key(request)
        response = await call_next(request)
        process_time = time.time() - start_time
        logger.info(f"Request processed in {process_time:.3f}s: {request.method} {request.url}")
        await self._cache_response(cache_key, response)
        return response
    
    def _generate_cache_key(self, request: Request) -> str:
        key_data = f"{request.method}:{request.url}:{request.headers.get('authorization','')}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    async def _cache_response(self, cache_key: str, response: Response):
        """Cache response for future use"""
        try:
            content_bytes: Optional[bytes] = None
            if hasattr(response, "body_iterator") and isinstance(response, StreamingResponse):
                # Buffer the iterator into bytes safely
                body = b""
                chunks = []
                async for chunk in response.body_iterator:  # type: ignore[attr-defined]
                    if isinstance(chunk, bytes):
                        chunks.append(chunk)
                    else:
                        chunks.append(chunk.encode())
                body = b"".join(chunks)
                content_bytes = body
                # Reset the iterator with an async generator
                async def _aiter() -> AsyncIterator[bytes]:
                    yield content_bytes  # type: ignore[misc]
                response.body_iterator = _aiter()  # type: ignore[attr-defined]
            elif hasattr(response, "body"):
                # FastAPI Response has .body attribute, not awaitable
                content_bytes = getattr(response, "body", None)
                if content_bytes is None and hasattr(response, "render"):
                    content_bytes = await response.render()
            if content_bytes is None:
                return
            self.cache[cache_key] = {
                "timestamp": time.time(),
                "content": content_bytes,
                "headers": dict(response.headers),
                "status_code": response.status_code,
            }
        except Exception as e:
            logger.debug(f"Skip caching due to error: {e}")
