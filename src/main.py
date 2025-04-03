import logging
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)

import contextlib
from fastapi import FastAPI, status
from fastapi_cache import FastAPICache, JsonCoder
from fastapi_cache.backends.redis import RedisBackend
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from redis.asyncio import from_url
from src.api.endpoints.auth import auth_router
from src.api.endpoints.orders import order_router
from src.kafka.producer import shutdown_kafka
from src.core.limiter import limiter
from src.core.config import settings


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI app.
    """
    redis = from_url(settings.FASTAPI_CACHE_REDIS_URL)
    FastAPICache.init(RedisBackend(redis), coder=JsonCoder)
    yield
    await redis.close()
    shutdown_kafka()


API_TITLE = "Order Management Service"
API_DESCRIPTION = """
Provides API endpoints for managing user orders.

Features:
- **User Authentication**: JWT-based authentication (Register and Login).
- **Order Management**: Create, retrieve, update orders.
- **Asynchronous Operations**: Uses Kafka for notifying about new orders.
- **Caching**: Caches order details using Redis for faster retrieval.
- **Rate Limiting**: Protects API endpoints from abuse.
"""
API_VERSION = "0.1.0"

common_responses = {
    status.HTTP_401_UNAUTHORIZED: {
        "description": "Authentication required"
    },
    status.HTTP_403_FORBIDDEN: {
        "description": "Not enough permissions"
    },
    status.HTTP_404_NOT_FOUND: {"description": "Resource not found"},
    status.HTTP_429_TOO_MANY_REQUESTS: {
        "description": "Rate limit exceeded (1 per second)",
    },
}

app = FastAPI(
    title=API_TITLE, description=API_DESCRIPTION, version=API_VERSION, lifespan=lifespan
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(
    auth_router,
    tags=["Authentication"],
    responses={
        429: common_responses[status.HTTP_429_TOO_MANY_REQUESTS],
        status.HTTP_400_BAD_REQUEST: {
            "description": "Invalid input or email already registered"
        },
        status.HTTP_401_UNAUTHORIZED: {"description": "Incorrect email or password"},
    },
)
app.include_router(
    order_router,
    prefix="/orders",
    tags=["Orders"],
    responses={
        401: common_responses[status.HTTP_401_UNAUTHORIZED],
        403: common_responses[status.HTTP_403_FORBIDDEN],
        404: common_responses[status.HTTP_404_NOT_FOUND],
        429: common_responses[status.HTTP_429_TOO_MANY_REQUESTS],
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Validation error in request data"
        },
    },
)

allowed_origins = ["http://localhost:3000", "http://127.0.0.1:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SlowAPIMiddleware)
