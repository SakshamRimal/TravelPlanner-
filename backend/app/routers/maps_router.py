from typing import Any

import httpx
from fastapi import APIRouter, Query, HTTPException

from app.core.config import get_settings

router = APIRouter(prefix="/maps", tags=["Maps"])
settings = get_settings()


@router.get("/search")
async def serp_search(q: str = Query(..., min_length=1), engine: str = "google", num: int = 10) -> Any:
    """Proxy endpoint to SerpApi search. Returns simplified results suitable for mapping.
    Example: GET /api/v1/maps/search?q=pokhara
    """
    if not settings.serpapi_api_key:
        raise HTTPException(status_code=500, detail="SERPAPI_API_KEY not configured on server")

    params = {"q": q, "engine": engine, "api_key": settings.serpapi_api_key, "num": num}

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get("https://serpapi.com/search.json", params=params)
            resp.raise_for_status()
            data = resp.json()
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc))

    results = []

    # Local results with coordinates
    local_places = data.get("local_results", {}).get("places", [])
    for place in local_places:
        results.append({
            "title": place.get("title"),
            "address": place.get("address"),
            "lat": place.get("gps_coordinates", {}).get("lat"),
            "lng": place.get("gps_coordinates", {}).get("lng"),
            "source": "local",
            "snippet": place.get("description") or place.get("subtitle"),
        })

    # Organic results fallback (may include snippets with lat/lng in maps links)
    for item in data.get("organic_results", [])[:num]:
        results.append({
            "title": item.get("title"),
            "snippet": item.get("snippet"),
            "url": item.get("link"),
            "source": "organic",
        })

    return {"query": q, "count": len(results), "results": results}
