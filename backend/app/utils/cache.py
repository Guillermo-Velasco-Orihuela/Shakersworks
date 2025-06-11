# backend/app/utils/cache.py

import redis
from app.config import settings
import json

# Single shared Redis client
_cache = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

def get_cache():
    return _cache

def cache_get(key: str):
    val = _cache.get(key)
    return json.loads(val) if val is not None else None

def cache_set(key: str, value, ttl: int = 300):
    # value will be JSON-serialized
    _cache.setex(key, ttl, json.dumps(value))
