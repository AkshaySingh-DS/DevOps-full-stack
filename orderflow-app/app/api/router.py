from fastapi import APIRouter

from app.api.routes import health, orders

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(orders.router)

health_router = APIRouter()
health_router.include_router(health.router)
