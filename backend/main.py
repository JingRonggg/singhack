import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.controller import documents

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

# Set specific module log levels
logging.getLogger("backend.tools.document_extractor").setLevel(logging.DEBUG)
logging.getLogger("backend.tools.format_validator").setLevel(logging.DEBUG)

poppler_path = r"C:\Program Files\poppler\Library\bin"
tesseract_path = r"C:\Program Files\Tesseract-OCR"

if poppler_path not in os.getenv("PATH", ""):
    os.environ["PATH"] = poppler_path + os.pathsep + os.environ.get("PATH", "")
if tesseract_path not in os.getenv("PATH", ""):
    os.environ["PATH"] = tesseract_path + os.pathsep + os.environ.get("PATH", "")

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
