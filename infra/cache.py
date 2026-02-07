import redis
import hashlib

from gateway.config import load_config


config = load_config()

REDIS_URL = config["cache"]["redis_url"]


class CacheClient:


    def __init__(self):

        self.client = redis.from_url(
            REDIS_URL,
            decode_responses=True
        )


    def _make_key(self, model: str, prompt: str) -> str:

        raw = f"{model}:{prompt}"

        return hashlib.sha256(raw.encode()).hexdigest()


    def get(self, model: str, prompt: str):

        key = self._make_key(model, prompt)

        return self.client.get(key)


    def set(self, model: str, prompt: str, value: str, ttl: int = 3600):

        key = self._make_key(model, prompt)

        self.client.setex(key, ttl, value)
