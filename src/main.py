import os

from dotenv import load_dotenv
from fastapi import FastAPI

from src.routes import app_router

load_dotenv()


app = FastAPI(
    title="OpenAI Agents Demo",
    debug=os.getenv("CURRENT_ENVIRONMENT", "") == "local",
)


app.include_router(app_router)
