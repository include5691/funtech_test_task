import logging
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)

import contextlib
from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from redis.asyncio import Redis
from src.api.endpoints.auth import auth_router
from src.api.endpoints.orders import order_router
from src.kafka.producer import shutdown_kafka
from src.core.limiter import limiter

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

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(auth_router)
app.include_router(order_router, prefix="/orders")

allowed_origins = ["http://localhost:3000", "http://127.0.0.1:3000"]

app.add_middleware(CORSMiddleware, 
                   allow_origins=allowed_origins,
                   allow_credentials=True,
                   allow_methods=["*"],
                   allow_headers=["*"])

app.add_middleware(SlowAPIMiddleware)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8000)