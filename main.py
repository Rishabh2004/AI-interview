from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.db.db import init_db, close_db_connection
from app.models.document_models import document_models
from fastapi.middleware.cors import CORSMiddleware
from app.core.logger import get_logger
from app.api import auth

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize database
    await init_db(document_models)
    yield
    # Shutdown: close database connection
    await close_db_connection()


app = FastAPI(title="AI Interview Backend", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)

logger.info("Application started")


@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"message": "AI Interview API is running"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="localhost", port=8000, log_level="info", reload=True)
