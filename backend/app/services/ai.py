from typing import Any

from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from app.core.config import get_settings
from app.schemas.ai import ItineraryGenerationResponse
from app.services.budget import BudgetService
from app.services.recommendations import RecommendationService


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
        destination = payload.get("destination", "")
        recommendations = await self.recommendations.get_recommendations(destination)
        days = 1
        if payload.get("start_date") and payload.get("end_date"):
            days = 3
        budget = await self.budget.estimate_budget(destination, days, payload.get("travelers", 1))
        return {
            "recommendations": recommendations,
            "budget_estimate": budget,
        }

    async def generate_itinerary(self, payload: dict[str, Any]) -> ItineraryGenerationResponse:
        parser = PydanticOutputParser(pydantic_object=ItineraryGenerationResponse)
        tool_context = await self._gather_tool_context(payload)
        prompt = PromptTemplate(
            template=(
                "You are a travel planner AI. Create a structured itinerary under Nepal only.\n"
                "{format_instructions}\n"
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
        return await chain.ainvoke({**payload, "tool_context": tool_context})
