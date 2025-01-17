import os

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

VALID_API_KEY = os.getenv("API_KEY")


class APIKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method == "OPTIONS":
            return await call_next(request)

        api_key = request.headers.get("API-KEY")

        if not api_key == VALID_API_KEY:
            return JSONResponse({"error": "Forbidden"}, status_code=403)

        return await call_next(request)
