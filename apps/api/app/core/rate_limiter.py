"""Sliding-window in-memory rate limiter with Redis upgrade capability."""

import time
from typing import Dict, List
from collections import defaultdict
from fastapi import Request

from .exceptions import RateLimitError
from .config import settings


class InMemoryRateLimiter:
    """Sliding-window rate limiter per client key (IP or user ID)."""

    def __init__(self):
        self.requests: Dict[str, List[float]] = defaultdict(list)

    def check(self, key: str, max_requests: int, window_seconds: int = 60) -> None:
        now = time.time()
        cutoff = now - window_seconds
        
        # Prune old timestamps
        self.requests[key] = [t for t in self.requests[key] if t > cutoff]

        # Periodic dictionary pruning to prevent memory growth
        if len(self.requests) > 5000:
            stale_keys = [k for k, timestamps in self.requests.items() if not timestamps or timestamps[-1] < cutoff]
            for k in stale_keys:
                del self.requests[k]

        if len(self.requests[key]) >= max_requests:
            raise RateLimitError(f"Rate limit exceeded ({max_requests} requests/min). Please wait before trying again.")

        self.requests[key].append(now)


limiter = InMemoryRateLimiter()


def rate_limit_dependency(max_requests: int = 60):
    """FastAPI dependency to rate limit endpoints."""
    async def dependency(request: Request):
        # Prefer user ID from request state if authenticated, else client host IP
        user_id = getattr(request.state, "user_id", None)
        client_ip = request.client.host if request.client else "unknown"
        key = f"rate:{user_id or client_ip}"
        limiter.check(key, max_requests=max_requests, window_seconds=60)
    return dependency
