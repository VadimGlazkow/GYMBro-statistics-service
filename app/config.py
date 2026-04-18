from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    NINJAS_API_KEY: str | None = None
    AI_SERVICE_URL: str
    TELEGRAM_SERVICE_URL: str

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()