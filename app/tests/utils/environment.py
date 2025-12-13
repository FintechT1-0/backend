from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    TEST_DATABASE_URL: str

    class Config:
        env_file = ".env.test"


settings = Settings()