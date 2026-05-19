from datetime import datetime
from typing import Any

from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from google.api_core.exceptions import ResourceExhausted

from app.core.config import get_settings
from app.schemas.ai_schema import ItineraryGenerationResponse
from app.services.budget_service import BudgetService
from app.services.recommendations_service import RecommendationService


class AIService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.recommendations = RecommendationService()
        self.budget = BudgetService()

    def _get_llm(self):
        return ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=self.settings.ai_temperature,
            google_api_key=self.settings.gemini_api_key,
        )

    async def _gather_tool_context(self, payload: dict[str, Any]) -> dict[str, Any]:
        origin = payload.get("origin", "")
        destination = payload.get("destination", "")
        travelers = payload.get("travelers", 1)

        start_str = payload.get("start_date")
        end_str = payload.get("end_date")

        if start_str and end_str:
            try:
                start = datetime.fromisoformat(start_str)
                end = datetime.fromisoformat(end_str)
                days = max(1, (end - start).days + 1)
            except ValueError:
                days = 1
        else:
            days = 1

        budget = await self.budget.estimate_budget(destination, days, travelers, origin=origin)
        budget_usd = budget.get("total_estimate", 0) / self.settings.usd_to_nrs_rate
        recommendations = await self.recommendations.get_recommendations(destination, origin=origin, budget=budget_usd)

        return {"recommendations": recommendations, "budget_estimate": budget}

    async def generate_itinerary(self, payload: dict[str, Any]) -> ItineraryGenerationResponse:
        parser = PydanticOutputParser(pydantic_object=ItineraryGenerationResponse)
        tool_context = await self._gather_tool_context(payload)

        prompt = PromptTemplate(
            template=(
                "You are a travel planner AI specializing in Nepal destinations. Create a detailed, hour-by-hour itinerary for travel within Nepal or to Nepal.\n"
                "{format_instructions}\n"
                "CRITICAL REQUIREMENTS:\n"
                "1. Each time period (morning, late_morning, afternoon, late_afternoon, evening) MUST have 2-3 sentences of detailed content.\n"
                "2. Each entry must include: specific time (e.g., 6:00 AM), exact location/place name, and detailed activity description.\n"
                "3. NEVER use short labels like 'Explore' or 'Free time' - provide actual planned activities.\n"
                "4. Include travel times between locations if relevant.\n"
                "Example format for each time slot:\n"
                "morning: '6:00 AM - Start from Kathmandu bus station. Take a tourist bus to Sauraha (6-7 hours, NPR 500-700). Arrive by 2:00 PM and check into jungle resort.'\n"
                "late_morning: '8:00 AM - Visit Elephant Breeding Center in Sauraha. Learn about elephant conservation (1-2 hours).'\n"
                "Provide this level of detail for EVERY time slot on EVERY day.\n"
                "Origin: {origin}\n"
                "Destination: {destination}\n"
                "Dates: {start_date} to {end_date}\n"
                "Travelers: {travelers}\n"
                "Budget: {budget}\n"
                "Interests: {interests}\n"
                "Transport: {transport}\n"
                "Accommodation: {accommodation}\n"
                "Notes: {additional_notes}\n"
                "Tool context: {tool_context}\n"
            ),
            input_variables=list(payload.keys()) + ["tool_context"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )

        llm = self._get_llm()
        chain = prompt | llm | parser
        try:
            return await chain.ainvoke({**payload, "tool_context": tool_context})
        except ResourceExhausted:
            return ItineraryGenerationResponse(
                summary="AI service is temporarily unavailable due to quota limits. Please try again later or contact support.",
                days=[],
                tips=["Check back tomorrow when the quota resets", "Contact support for assistance"],
                estimated_total=None
            )
