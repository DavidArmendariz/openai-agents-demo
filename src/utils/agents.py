import datetime

from agents import Agent, function_tool

from src.utils.prompts import agent_prompt
from src.utils.schedule_meeting import schedule_meeting


@function_tool
def get_current_time_tool() -> str:
    now = datetime.datetime.now()
    return f"La hora actual es {now.strftime('%Y-%m-%d %H:%M:%S')}"


@function_tool
async def schedule_meeting_tool(
    start_datetime: str, subject: str, recipients: list[str]
) -> str:
    result = await schedule_meeting(
        {"start_datetime": start_datetime, "subject": subject, "recipients": recipients}
    )
    return "Cita programada con éxito" if result else "Error al programar la cita"


legal_agent = Agent(
    name="Agente Legal",
    instructions=agent_prompt,
    tools=[get_current_time_tool, schedule_meeting_tool],
)

__all__ = ["legal_agent"]
