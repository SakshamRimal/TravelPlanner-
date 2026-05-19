from datetime import datetime, timezone

from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from google.api_core.exceptions import ResourceExhausted

from app.core.config import get_settings
from app.schemas.chat_schema import ChatResponse


class ChatService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def _get_llm(self):
        return ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.7,
            google_api_key=self.settings.gemini_api_key,
        )

    async def reply(self, message: str, context: str | None = None) -> ChatResponse:
        prompt = PromptTemplate.from_template(
            "You are a helpful Nepal travel assistant. Answer user questions about travel planning.\n"
            "User message: {message}\n"
            "Context: {context}\n"
            "Provide a helpful, concise response about Nepal travel."
        )

        llm = self._get_llm()
        chain = prompt | llm

        context_str = context or "No trip context available"

        try:
            response = await chain.ainvoke({"message": message, "context": context_str or "No trip context available"})
            reply_text = response.content if hasattr(response, 'content') else str(response)
        except ResourceExhausted:
            reply_text = (
                "I've reached my daily limit for AI responses. Please try again tomorrow or "
                "contact us for immediate assistance with your Nepal travel planning. "
                "You can still browse destinations, hotels, and flights independently."
            )

        return ChatResponse(reply=reply_text.strip(), created_at=datetime.now(timezone.utc))