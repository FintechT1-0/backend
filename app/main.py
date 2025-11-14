from app.environment import Settings
settings = Settings()

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
from app.database import Base, engine

from app.auth.routes import auth_router
from app.courses.routes import course_router


Base.metadata.create_all(bind=engine)         
app = FastAPI()


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.debug(str(exc))
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