import json

import redis
from app.core.config import settings

# Initialize a single shared Redis client using the URL from settings
_cache = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)


def get_cache() -> redis.Redis:
    """
    Return the shared Redis client instance.
    """
    return _cache


def cache_get(key: str) -> object | None:
    """
    Retrieve a JSON-deserialized value from Redis by key.

    Args:
        key: The cache key.

    Returns:
        The deserialized Python object, or None if the key is missing.
    """
    val = _cache.get(key)
    if val is None:
        return None
    return json.loads(val)


def cache_set(key: str, value: object, ttl: int = 300) -> None:
    """
    Set a JSON-serialized value in Redis with an expiration TTL.

    Args:
        key: The cache key.
        value: The Python object to serialize and store.
        ttl: Time-to-live in seconds.
    """
    # Serialize the value to JSON and store it with expiration
    _cache.setex(key, ttl, json.dumps(value))
