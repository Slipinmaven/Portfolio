from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.db.session import create_engine, create_session_factory
from app.middleware.logging import AccessLoggingMiddleware
from app.middleware.request_context import RequestContextMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    configure_logging(settings.log_level)
    app.state.engine = create_engine(settings)
    app.state.session_factory = create_session_factory(app.state.engine)
    yield
    await app.state.engine.dispose()


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)
    application.add_middleware(RequestContextMiddleware)
    application.add_middleware(AccessLoggingMiddleware)
    application.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, allow_credentials=True, allow_methods=["GET", "POST"], allow_headers=["Authorization", "Content-Type", "X-Request-ID"])
    application.include_router(router)
    return application


app = create_app()
