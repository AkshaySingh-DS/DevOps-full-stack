from fastapi import FastAPI

from app.api.router import api_router, health_router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Simple Order Management API for the OrderFlow platform project.",
)

app.include_router(health_router)
app.include_router(api_router)
