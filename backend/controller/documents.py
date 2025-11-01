from fastapi import APIRouter, UploadFile, File, HTTPException
from uuid import uuid4
import os

from backend.services.document_extractor import extract_with_unstructured
from backend.services.format_validator import run_format_validation
from backend.tools.image_analysis import image_analysis

router = APIRouter()
UPLOAD_DIR = "data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/")
async def upload_and_validate(file: UploadFile = File(...)):
    """
    Upload and validate documents (PDF, TXT, XLSX) or images.

    Supported file types:
    - Documents: .pdf, .txt, .xlsx, .xls
    - Images: .jpg, .jpeg, .png, .bmp, .tiff, .webp
    """
    # Validate file type
    allowed_extensions = {
        ".pdf",
        ".txt",
        ".xlsx",
        ".xls",  # Documents
        ".jpg",
        ".jpeg",
        ".png",
        ".bmp",
        ".tiff",
        ".webp",  # Images
    }
    file_ext = os.path.splitext(file.filename)[1].lower()

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: {', '.join(sorted(allowed_extensions))}",
        )

    # Save file
    file_id = str(uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")
    with open(file_path, "wb") as f:
        f.write(await file.read())

    try:
        # Use Unstructured for document/image text extraction (PDF, TXT, XLSX, Images with OCR)
        elements, full_text, metadata = extract_with_unstructured(file_path)

        # Run Python-based format validation on extracted text
        format_report = run_format_validation(full_text, file_path)

        # Check if it's an image file for appropriate labeling
        image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"}
        file_type = "image" if file_ext in image_extensions else "document"

        # Construct and return JSON response
        response = {
            "file_id": file_id,
            "filename": file.filename,
            "file_type": file_type,
            "document_metadata": metadata,
            "document_structure": {
                "headers": [
                    e.text
                    for e in elements
                    if hasattr(e, "category") and e.category in ("Title", "Header")
                ],
                "paragraph_count": sum(
                    1
                    for e in elements
                    if hasattr(e, "category") and e.category == "Paragraph"
                ),
            },
            "format_validation": format_report,
        }

        return response

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Clean up file if processing failed
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


@router.post("/image")
async def upload_and_analyze_image(file: UploadFile = File(...)):
    """
    Upload an image file and perform comprehensive forensic analysis.

    Features:
    - Authenticity verification
    - AI-generated detection
    - Tampering detection
    - Forensic analysis with metadata and pixel-level inspection
    """
    # Validate file type
    allowed_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"}
    file_ext = os.path.splitext(file.filename)[1].lower()

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: {', '.join(allowed_extensions)}",
        )

    # Save file
    file_id = str(uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")

    try:
        with open(file_path, "wb") as f:
            f.write(await file.read())

        # Run image analysis
        analysis_result = image_analysis.invoke({"image_path": file_path})

        # Check if there was an error in the analysis
        if "error" in analysis_result:
            raise HTTPException(
                status_code=500,
                detail=f"Image analysis failed: {analysis_result['error']}",
            )

        # Construct response
        response = {
            "file_id": file_id,
            "filename": file.filename,
            "file_path": file_path,
            "analysis": {
                "authenticity": {
                    "score": analysis_result["authenticity_score"],
                    "status": (
                        "authentic"
                        if analysis_result["authenticity_score"] >= 70
                        else (
                            "suspicious"
                            if analysis_result["authenticity_score"] >= 40
                            else "likely_fraudulent"
                        )
                    ),
                },
                "ai_detection": {
                    "is_ai_generated": analysis_result["is_ai_generated"],
                    "confidence": analysis_result["ai_confidence"],
                    "risk_level": (
                        "high"
                        if analysis_result["is_ai_generated"]
                        and analysis_result["ai_confidence"] >= 70
                        else "medium"
                        if analysis_result["is_ai_generated"]
                        else "low"
                    ),
                },
                "tampering": {
                    "is_tampered": analysis_result["is_tampered"],
                    "indicators": analysis_result["tampering_indicators"],
                    "indicator_count": len(analysis_result["tampering_indicators"]),
                },
                "forensics": {
                    "metadata": analysis_result["metadata_analysis"],
                    "findings": analysis_result["forensic_findings"],
                },
                "reverse_search": {
                    "results": analysis_result.get("reverse_search_results", {}),
                    "summary": {
                        "match_status": analysis_result.get(
                            "reverse_search_results", {}
                        ).get("match_status", "UNKNOWN"),
                        "verdict": analysis_result.get(
                            "reverse_search_results", {}
                        ).get("verdict", "No verdict available"),
                        "exact_match": analysis_result.get(
                            "reverse_search_results", {}
                        ).get("exact_match")
                        == "True",
                        "similarity": analysis_result.get(
                            "reverse_search_results", {}
                        ).get("perceptual_similarity", "N/A"),
                    },
                },
                "recommendations": analysis_result["recommendations"],
                "timestamp": analysis_result["timestamp"],
            },
        }

        return response

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Clean up file if processing failed
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=500, detail=f"Image processing failed: {str(e)}"
        )
