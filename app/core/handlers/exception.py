from typing import cast

from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.exceptions.base import AppError


async def global_app_error_handler(
    request: Request,
    exc: Exception
) -> JSONResponse:
    custom_exc = cast(AppError, exc)

    return JSONResponse(
        status_code=custom_exc.status_code if custom_exc.status_code is not None else 500,
        content={
            "status": custom_exc.status_code,
            "code": custom_exc.error_code,
            "message": custom_exc.message,
            "details": custom_exc.details
        }
    )
