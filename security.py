import time
from collections import defaultdict, deque

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

WINDOW = 60
LIMITS = {
    "/auth/login": 8,
    "/auth/register": 5,
}


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.hits = defaultdict(deque)

    async def dispatch(self, request, call_next):
        path = request.url.path
        limit = LIMITS.get(path)
        if limit:
            ip = request.client.host if request.client else "unknown"
            key = f"{ip}:{path}"
            now = time.time()
            bucket = self.hits[key]
            while bucket and now - bucket[0] > WINDOW:
                bucket.popleft()
            if len(bucket) >= limit:
                return JSONResponse(
                    {"error": "Too many attempts. Please wait and try again."},
                    status_code=429,
                )
            bucket.append(now)
        return await call_next(request)
