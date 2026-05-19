import random
import time
from typing import DefaultDict, Tuple

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, limit: int = 100, window_seconds: int = 60):
        super().__init__(app)
        self.limit = limit
        self.window = window_seconds
        self.hits: DefaultDict[str, Tuple[int, float]] = {}

    async def dispatch(self, request: Request, call_next):
        ip = request.client.host if request.client else "anonymous"
        now = time.time()

        if random.random() < 0.01:
            expired_keys = [
                key for key, (_, start_time) in self.hits.items()
                if now - start_time > self.window
            ]
            for key in expired_keys:
                del self.hits[key]

        count, start = self.hits.get(ip, (0, now))
        if now - start > self.window:
            count, start = 0, now
        count += 1
        self.hits[ip] = (count, start)
        if count > self.limit:
            return JSONResponse({"detail": "Rate limit exceeded"}, status_code=429)
        return await call_next(request)
