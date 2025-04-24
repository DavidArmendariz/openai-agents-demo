from fastapi import APIRouter

from src.api import chatbot

# Authorize requests here
app_router = APIRouter()
app_router.include_router(chatbot.router)
