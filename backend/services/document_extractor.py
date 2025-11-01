from unstructured.partition.auto import partition
from unstructured.documents.elements import Text
import logging

logger = logging.getLogger(__name__)


def extract_with_unstructured(file_path: str):
    """
    Extracts structured elements, plain text, and metadata from a document using Unstructured.
    """
    logger.info(f"Starting extraction for file: {file_path}")

    elements = partition(file_path)
    logger.info(f"Partitioned document into {len(elements)} elements")

    full_text = "\n".join(
        [el.text for el in elements if isinstance(el, Text) and el.text]
    )

    logger.info(f"Extracted text preview (first 500 chars): {full_text[:500]}")
    logger.info(f"Total extracted text length: {len(full_text)} characters")
    logger.debug(f"Full extracted text:\n{full_text}")

    metadata = {
        "file_type": file_path.split(".")[-1],
        "page_count": len(
            set(
                [
                    el.metadata.page_number
                    for el in elements
                    if el.metadata and el.metadata.page_number
                ]
            )
        ),
        "total_text_length": len(full_text),
    }

    return elements, full_text, metadata
