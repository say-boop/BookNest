from fastapi import FastAPI

from app.core.exceptions.base import AppError
from app.core.handlers.exception import global_app_error_handler
from app.features.books.router import router_books
from app.features.users.router import router_users


app = FastAPI()

app.add_exception_handler(AppError, global_app_error_handler)

app.include_router(router_books)
app.include_router(router_users)


@app.get("/health")
async def health():
    return {
        "status": "ok"
    }