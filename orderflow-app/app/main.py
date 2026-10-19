from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

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


# Keep metric labels low-cardinality: the instrumentator groups status codes and
# uses FastAPI route templates instead of raw URL paths. /metrics is excluded
# from its own request counters and is deliberately not added to OpenAPI docs.
Instrumentator(
    should_group_status_codes=True,
    should_ignore_untemplated=True,
    excluded_handlers=["/metrics"],
).instrument(app).expose(
    app,
    endpoint="/metrics",
    include_in_schema=False,
    should_gzip=True,
)