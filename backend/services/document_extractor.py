from unstructured.partition.auto import partition
from unstructured.partition.text import partition_text
from unstructured.partition.image import partition_image
import logging
import os

logger = logging.getLogger(__name__)


def extract_with_unstructured(file_path: str):
    """
    Extracts structured elements, plain text, and metadata from various document types using Unstructured.

    Supported formats:
    - PDF documents
    - Text files (.txt)
    - Excel files (.xlsx, .xls)
    - Images with OCR (.jpg, .jpeg, .png, .bmp, .tiff, .webp)
    - Word documents (.doc, .docx)
    """
    logger.info(f"Starting extraction for file: {file_path}")

    # Get file extension
    file_ext = os.path.splitext(file_path)[1].lower()

    # Handle different file types
    try:
        if file_ext == ".txt":
            # For plain text files, use partition_text for better handling
            logger.info("Detected text file, using text partition")
            elements = partition_text(filename=file_path)
        elif file_ext in [".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"]:
            # For images, use partition_image with OCR
            logger.info("Detected image file, using image partition with OCR")
            elements = partition_image(filename=file_path)
        else:
            # For PDF, XLSX, DOCX and other formats, use auto partition
            logger.info(f"Using auto partition for {file_ext} file")
            elements = partition(file_path)

        logger.info(f"Partitioned document into {len(elements)} elements")
    except Exception as e:
        logger.error(f"Error partitioning file: {str(e)}")
        raise

    # Extract full text from elements
    full_text = "\n".join(
        [el.text for el in elements if hasattr(el, "text") and el.text]
    )

    logger.info(f"Extracted text preview (first 500 chars): {full_text[:500]}")
    logger.info(f"Total extracted text length: {len(full_text)} characters")
    logger.debug(f"Full extracted text:\n{full_text}")

    # Calculate page count (handle cases where page_number might not exist)
    page_numbers = set()
    for el in elements:
        if (
            hasattr(el, "metadata")
            and el.metadata
            and hasattr(el.metadata, "page_number")
            and el.metadata.page_number
        ):
            page_numbers.add(el.metadata.page_number)

    # For text files and single-page images, default to 1 page if no page_number found
    page_count = len(page_numbers) if page_numbers else 1

    metadata = {
        "file_type": file_ext.lstrip("."),
        "page_count": page_count,
        "total_text_length": len(full_text),
    }

    return elements, full_text, metadata
