from redis import asyncio as aioredis
from typing import AsyncGenerator

from app.core.config import settings


REDIS_URL = settings.get_redis_url()


async def get_redis() -> AsyncGenerator[aioredis.Redis, None]:
    client = aioredis.from_url(REDIS_URL, decode_responses=True)

    try:
        yield client
    finally:
        await client.aclose()