from datetime import datetime

from app.schemas.chat import ChatResponse


class ChatService:
    async def reply(self, message: str) -> ChatResponse:
        reply = (
            "I can help plan that trip. Share your dates, budget, and interests "
            "for a tailored itinerary."
        )
        return ChatResponse(reply=reply, created_at=datetime.utcnow())
