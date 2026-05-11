class BudgetService:
    async def estimate_budget(self, destination: str, days: int, travelers: int):
        base = 40 * days * travelers
        return {
            "currency": "NRS",
            "total_estimate": base + 200,
            "breakdown": "Flights, stay, food, activities",
        }
