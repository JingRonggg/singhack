from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.controller import documents
from backend.util.logging_config import setup_logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
setup_logging()

app = FastAPI(
    title="singhack",
    description="singhack",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(documents.router, prefix="/api/upload")


@app.get("/")
async def root():
    return {"message": "Hello, FastAPI!"}
