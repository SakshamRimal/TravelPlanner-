import time
from collections import defaultdict
from typing import DefaultDict, Tuple

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, limit: int = 100, window_seconds: int = 60):
        super().__init__(app)
        self.limit = limit
        self.window = window_seconds
        self.hits: DefaultDict[str, Tuple[int, float]] = defaultdict(lambda: (0, 0.0))

    async def dispatch(self, request: Request, call_next):
        ip = request.client.host if request.client else "anonymous"
        count, start = self.hits[ip]
        now = time.time()
        if now - start > self.window:
            count, start = 0, now
        count += 1
        self.hits[ip] = (count, start)
        if count > self.limit:
            return JSONResponse({"detail": "Rate limit exceeded"}, status_code=429)
        return await call_next(request)
