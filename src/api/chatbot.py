from agents import Runner
from fastapi import APIRouter
from pydantic import BaseModel

from src.utils.agents import legal_agent

router = APIRouter()


class ChatbotParams(BaseModel):
    message: str
    session_id: str | None = None


@router.post("/chatbot")
async def chatbot(request_body: ChatbotParams):
    result = await Runner.run(legal_agent, request_body.message)
    return {"response": result.final_output}
