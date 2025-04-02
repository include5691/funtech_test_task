import logging
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)

import contextlib
from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis.asyncio import Redis
from src.api.endpoints.auth import auth_router
from src.api.endpoints.orders import order_router
from src.kafka.producer import shutdown_kafka

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI app.
    """
    redis = Redis()
    FastAPICache.init(RedisBackend(redis))
    yield
    await redis.close()
    shutdown_kafka()

app = FastAPI(lifespan=lifespan)
app.include_router(auth_router)
app.include_router(order_router, prefix="/orders")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8000)