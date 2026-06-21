from app.core.logging_config import setup_logging
from fastapi import FastAPI
from app.routers.v1 import auth
from app.routers.v1 import health
from app.routers.v1 import settings as settings_router
from app.core.config import settings
from fastapi.exceptions import RequestValidationError
from app.core.middleware import RequestContextMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.exceptions.handlers import (
    app_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    generic_exception_handler,
)
from app.exceptions.custom_exception import AppException

setup_logging()

if settings.is_production:
    docs_url = None
    redoc_url = None
    openapi_url = None
else:
    docs_url = "/docs"
    redoc_url = "/redoc"
    openapi_url = "/openapi.json"

app = FastAPI(
    title="Authentication Service",
    docs_url=docs_url,
    redoc_url=redoc_url,
    openapi_url=openapi_url,
)


app.add_middleware(RequestContextMiddleware)

app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

app.include_router(health.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(settings_router.router, prefix="/api/v1")
