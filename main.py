from fastapi.concurrency import asynccontextmanager
from fastapi import FastAPI
from app.db.prisma import connect_db, disconnect_db
from fastapi.middleware.cors import CORSMiddleware
# from app.core.logger import get_logger
from app.api.auth.routes import auth
from app.db.memory import init_mem0
# logger = get_logger(__name__)
from app.api.interview.routes import interview

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize database
    await connect_db()
    # Intializwe Mem0
    await init_mem0()
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
app.include_router(interview)

print("Application started")


@app.get("/")
async def root():
    print("Root endpoint accessed")
    return {"message": "AI Interview API is running"}
