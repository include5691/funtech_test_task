from slowapi import Limiter
from slowapi.util import get_remote_address
from src.core.config import settings

limiter = Limiter(key_func=get_remote_address, default_limits=["1/second"], storage_uri=settings.SLOWAPI_REDIS_URL)