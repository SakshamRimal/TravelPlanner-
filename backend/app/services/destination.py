class DestinationService:
    async def search(self, query: str):
        results = [
            {"name": "Pokhara", "country": "Nepal"},
            {"name": "Kyoto", "country": "Japan"},
            {"name": "Lisbon", "country": "Portugal"},
        ]
        return [item for item in results if query.lower() in item["name"].lower()]
