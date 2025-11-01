from fastapi import APIRouter, UploadFile, File, HTTPException
from uuid import uuid4
import os

from backend.tools.document_extractor import extract_with_unstructured
from backend.tools.format_validator import run_format_validation

router = APIRouter()
UPLOAD_DIR = "data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/")
async def upload_and_validate(file: UploadFile = File(...)):
    # 1️⃣ Save file
    file_id = str(uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")
    with open(file_path, "wb") as f:
        f.write(await file.read())

    try:
        # 2️⃣ Use Unstructured for extraction
        elements, full_text, metadata = extract_with_unstructured(file_path)

        # 3️⃣ Run Python-based format validation
        format_report = run_format_validation(full_text, file_path)

        # 4️⃣ Construct and return JSON response
        response = {
            "file_id": file_id,
            "document_metadata": metadata,
            "document_structure": {
                "headers": [
                    e.text for e in elements if e.category in ("Title", "Header")
                ],
                "paragraph_count": sum(
                    1 for e in elements if e.category == "Paragraph"
                ),
            },
            "format_validation": format_report,
        }

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
