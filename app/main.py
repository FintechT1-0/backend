from app.environment import settings
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
from app.database import Base, engine
from jinja2 import Environment, FileSystemLoader

from app.api.auth.routes import auth_router
from app.api.courses.routes import course_router
from app.api.insights.routes import insights_router
from app.api.telemetry.routes import telemetry_router

import os
import app.template_storage as template_storage

      
app = FastAPI()


@app.on_event("startup")
async def startup_init():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    template_dir = os.path.join(os.path.dirname(__file__), "email_templates")

    template_storage.env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=True
    )

    for filename in os.listdir(template_dir):
        if filename.endswith(".html"):
            template_name = os.path.splitext(filename)[0]
            template_storage.templates[template_name] = template_storage.env.get_template(filename)

    logger.debug(f"Loaded email templates: {list(template_storage.templates.keys())}")


@app.on_event("startup")
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.critical(f"Critical uncaught error: {str(exc)}")
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"detail": "Unexpected error."})


app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.TRUSTED_ORIGIN if not settings.CORS_DEBUG_MODE else "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router, prefix="/auth")
app.include_router(course_router, prefix="/courses")
app.include_router(insights_router, prefix="/insights")
app.include_router(telemetry_router, prefix="/telemetry")