from typing import Any

import httpx

from app.core.config import get_settings


class DestinationService:
    def __init__(self) -> None:
        self.settings = get_settings()

    async def search(self, query: str) -> list[dict[str, Any]]:
        """
        Search for destinations using SerpApi Google Local search.
        Uses Nepal-specific queries when no location is specified.
        """
        if not self.settings.serpapi_api_key:
            return []

        async with httpx.AsyncClient(timeout=10) as client:
            params = {
                "q": f"{query} city tourist destination",
                "engine": "google",
                "api_key": self.settings.serpapi_api_key,
                "num": 10,
            }
            resp = await client.get("https://serpapi.com/search.json", params=params)
            resp.raise_for_status()
            data = resp.json()

        results = []
        for item in data.get("organic_results", [])[:10]:
            results.append({
                "name": item.get("title", "").split(" - ")[0],
                "country": item.get("title", "").split(" - ")[-1] if " - " in item.get("title", "") else "",
                "description": item.get("snippet", ""),
                "url": item.get("link", ""),
            })

        return results
