import datetime

from agents import Agent, Runner, function_tool
from fastapi import APIRouter
from pydantic import BaseModel


@function_tool
def get_weather(city: str) -> str:
    return f"The weather in {city} is sunny."


@function_tool
def get_current_time() -> str:
    now = datetime.datetime.now()
    return f"The current time is {now.strftime('%Y-%m-%d %H:%M:%S')}"


agent = Agent(
    name="Lawyers Agent",
    instructions="You are a helpful agent.",
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
