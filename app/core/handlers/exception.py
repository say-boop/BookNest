from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.exceptions.base import AppError


async def global_app_error_handler(
    request: Request,
    exc: AppError
):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": exc.status_code,
            "code": exc.error_code,
            "message": exc.message,
            "details": exc.details
        }
    )