from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware
import logging
import json
from datetime import datetime

class CustomLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        if response.status_code >= 400:
            logging.error(json.dumps({
                "timestamp": datetime.now().isoformat(),
                "level": "ERROR",
                "method": request.method,
                "path": request.url.path,
                "error": response.body.decode() if hasattr(response, 'body') else "",
                "status_code": response.status_code
            }))

        return response

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logging.error(json.dumps({
        "timestamp": datetime.now().isoformat(),
        "level": "ERROR",
        "method": request.method,
        "path": request.url.path,
        "error": "Validation Error",
        "details": str(exc)
    }))
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "body": exc.body}
    )

async def http_exception_handler(request: Request, exc):
    logging.error(json.dumps({
        "timestamp": datetime.now().isoformat(),
        "level": "ERROR",
        "method": request.method,
        "path": request.url.path,
        "error": str(exc),
        "status_code": exc.status_code
    }))
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": str(exc)}
    )

async def general_exception_handler(request: Request, exc: Exception):
    logging.error(json.dumps({
        "timestamp": datetime.now().isoformat(),
        "level": "ERROR",
        "method": request.method,
        "path": request.url.path,
        "error": str(exc),
        "type": type(exc).__name__
    }))
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected error occurred."}
    )