from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.controller import documents, web_scraper, evaluation, dashboard
from backend.util.logging_config import setup_logging

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
app.include_router(web_scraper.router, prefix="/api/scraper")
app.include_router(evaluation.router, prefix="/api/evaluation")
app.include_router(dashboard.router, prefix="/api/dashboard")


@app.get("/")
async def root():
    return {"message": "Hello, FastAPI!"}
