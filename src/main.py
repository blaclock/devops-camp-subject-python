from contextlib import asynccontextmanager
from fastapi import FastAPI

from src.db.database import create_db_and_tables

from src.api.routes.reservations import router as reservation_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(reservation_router, prefix="/reservations", tags=["reservations"])


@app.get("/health")
def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":

    import os

    reload = os.getenv("UVICORN_RELOAD", "1").lower() in ("1", "true", "yes")

    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=reload)
