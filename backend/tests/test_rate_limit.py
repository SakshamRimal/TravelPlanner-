import pytest
import time
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.utils.rate_limit import RateLimitMiddleware


@pytest.mark.asyncio
async def test_rate_limit_allows_requests_under_limit():
    app = RateLimitMiddleware.__new__(RateLimitMiddleware)
    app.limit = 100
    app.window = 60
    app.hits = {}

    async def call_next(request):
        return JSONResponse({"status": "ok"})

    request = Request(scope={"type": "http", "client": ("127.0.0.1", 8000), "method": "GET", "path": "/"})
    response = await app.dispatch(request, call_next)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_rate_limit_blocks_excessive_requests():
    app = RateLimitMiddleware.__new__(RateLimitMiddleware)
    app.limit = 2
    app.window = 60
    app.hits = {}

    async def call_next(request):
        return JSONResponse({"status": "ok"})

    request = Request(scope={"type": "http", "client": ("127.0.0.1", 8000), "method": "GET", "path": "/"})

    await app.dispatch(request, call_next)
    await app.dispatch(request, call_next)

    response = await app.dispatch(request, call_next)
    assert response.status_code == 429


@pytest.mark.asyncio
async def test_rate_limit_window_reset():
    app = RateLimitMiddleware.__new__(RateLimitMiddleware)
    app.limit = 2
    app.window = 1
    app.hits = {"127.0.0.1": (2, time.time() - 2)}

    async def call_next(request):
        return JSONResponse({"status": "ok"})

    request = Request(scope={"type": "http", "client": ("127.0.0.1", 8000), "method": "GET", "path": "/"})
    response = await app.dispatch(request, call_next)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_rate_limit_cleanup_on_sample():
    app = RateLimitMiddleware.__new__(RateLimitMiddleware)
    app.limit = 100
    app.window = 1
    app.hits = {"old_ip": (50, time.time() - 10)}

    async def call_next(request):
        return JSONResponse({"status": "ok"})

    request = Request(scope={"type": "http", "client": ("127.0.0.1", 8000), "method": "GET", "path": "/"})
    await app.dispatch(request, call_next)

    assert "old_ip" not in app.hits or app.hits.get("old_ip", (0, 0))[1] > time.time() - 10