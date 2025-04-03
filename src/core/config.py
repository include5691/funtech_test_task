import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file='.env',
        extra='ignore'
    )

    SECRET_KEY: str

    DATABASE_URL: str

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"

    KAFKA_BOOTSTRAP_SERVERS: str
    KAFKA_NEW_ORDERS_TOPIC: str = "new-orders"

    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    SLOWAPI_REDIS_URL: str

    FASTAPI_CACHE_REDIS_URL: str

settings = Settings()