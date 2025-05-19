from fastapi.concurrency import asynccontextmanager
from fastapi import FastAPI
from app.db.prisma import connect_db, disconnect_db
from fastapi.middleware.cors import CORSMiddleware
from app.core.logger import get_logger
from app.api.auth.routes import auth

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize database
    await connect_db()
    yield
    # Shutdown: close database connection
    await disconnect_db()


app = FastAPI(title="AI Interview Backend", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth)

logger.info("Application started")


@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"message": "AI Interview API is running"}
