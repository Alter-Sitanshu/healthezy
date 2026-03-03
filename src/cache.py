import redis
import json
from typing import Any, Optional

# Initialize Redis client
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

def set_cache(key: str, value: Any, expiry: int = 3600) -> None:
    """Set a value in the cache with an optional expiry time."""
    redis_client.set(key, json.dumps(value), ex=expiry)

def get_cache(key: str) -> Optional[Any]:
    """Retrieve a value from the cache."""
    value = redis_client.get(key)
    return json.loads(value) if value else None #type: ignore

def delete_cache(key: str) -> None:
    """Delete a value from the cache."""
    redis_client.delete(key)