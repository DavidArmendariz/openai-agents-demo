import datetime

from agents import Agent, Runner, function_tool
from fastapi import APIRouter
from pydantic import BaseModel

from src.utils.prompts import agent_prompt


@function_tool
def get_weather(city: str) -> str:
    return f"El clima en {city} está soleado."


@function_tool
def get_current_time() -> str:
    now = datetime.datetime.now()
    return f"La hora actual es {now.strftime('%Y-%m-%d %H:%M:%S')}"


agent = Agent(
    name="Agente Legal",
    instructions=agent_prompt,
    tools=[get_weather, get_current_time],
)

router = APIRouter()


class ChatbotParams(BaseModel):
    message: str
    session_id: str | None = None


@router.post("/chatbot")
async def chatbot(request_body: ChatbotParams):
    result = await Runner.run(agent, request_body.message)
    return {"response": result.final_output}
