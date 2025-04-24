import datetime

from agents import Agent, function_tool

from src.utils.prompts import agent_prompt


@function_tool
def get_current_time() -> str:
    now = datetime.datetime.now()
    return f"La hora actual es {now.strftime('%Y-%m-%d %H:%M:%S')}"


legal_agent = Agent(
    name="Agente Legal",
    instructions=agent_prompt,
    tools=[get_current_time],
)

__all__ = ["legal_agent"]
