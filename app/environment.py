from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    CORS_DEBUG_MODE: bool
    TRUSTED_ORIGIN: str
    ADMIN_PASSWORD: str
    DB_CONNECTION_LIMIT: int
    WORKERS: int

    class Config:
        env_file = ".env"


settings = Settings()