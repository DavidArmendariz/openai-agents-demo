import datetime

from agents import Agent, ModelSettings, enable_verbose_stdout_logging, function_tool

from src.utils.prompts import agent_prompt
from src.utils.schedule_meeting import schedule_meeting

enable_verbose_stdout_logging()


@function_tool
def get_current_time_tool() -> str:
    """
    Obtiene la fecha y hora actual.
    Útil cuando el usuario pregunta o necesita la hora o fecha actual.
    Regresa la información en formato 'YYYY-MM-DD HH:MM:SS'
    """
    now = datetime.datetime.now()
    return f"La hora actual es {now.strftime('%Y-%m-%d %H:%M:%S')}"


@function_tool
async def schedule_meeting_tool(
    start_datetime: str, subject: str, recipients: list[str]
) -> str:
    """
    Programa una cita con un abogado de la firma.

    Parámetros:
    - start_datetime: Fecha y hora de inicio en formato ISO 8601 (YYYY-MM-DDTHH:MM:SSZ)
    - subject: Asunto o título de la reunión
    - recipients: Lista de teléfonos de los participantes

    La cita tendrá una duración de 30 minutos y se creará automáticamente
    como una reunión virtual de Teams. Usar este método cuando el usuario
    desee agendar una consulta con algún abogado.
    """
    result = await schedule_meeting(
        {"start_datetime": start_datetime, "subject": subject, "recipients": recipients}
    )
    return (
        "Cita programada con éxito. Revisa la notificación en tu celular."
        if result
        else "Error al programar la cita"
    )


legal_agent = Agent(
    name="Agente Legal",
    instructions=agent_prompt,
    tools=[get_current_time_tool, schedule_meeting_tool],
    model_settings=ModelSettings(max_tokens=100),
)

__all__ = ["legal_agent"]
