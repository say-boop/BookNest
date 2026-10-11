from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.core.exceptions.base import AppError
from app.core.handlers.exception import global_app_error_handler
from app.core.database import engine, init_db
from app.features.books.router import router_books


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)

app.add_exception_handler(AppError, global_app_error_handler)

app.include_router(router_books)


@app.get("/health")
async def health():
    return {
        "status": "ok"
    }