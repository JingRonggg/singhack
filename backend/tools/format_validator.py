import fitz  # PyMuPDF
import os
import re
from spellchecker import SpellChecker
import logging

logger = logging.getLogger(__name__)


def detect_double_spacing(text):
    """Detect double newlines or large line gaps in extracted text."""
    if not text:
        return 0
    # Count occurrences of double newlines
    double_newline_count = text.count("\n\n")
    return double_newline_count


def detect_irregular_fonts(pdf_path):
    """Check if multiple font families or sizes are used."""
    doc = fitz.open(pdf_path)
    fonts = []
    for page in doc:
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            for line in b.get("lines", []):
                for span in line.get("spans", []):
                    fonts.append((span["font"], round(span["size"], 1)))
    unique_fonts = set(f[0] for f in fonts)
    unique_sizes = set(f[1] for f in fonts)
    return {
        "unique_fonts": list(unique_fonts),
        "unique_font_count": len(unique_fonts),
        "unique_font_sizes": list(unique_sizes),
        "font_size_variants": len(unique_sizes),
    }


def detect_indentation_issues(pdf_path):
    """Check left margin variance between paragraphs (requires direct PDF access)."""
    if not pdf_path or not os.path.exists(pdf_path):
        return None

    doc = fitz.open(pdf_path)
    left_margins = []
    for page in doc:
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            if b.get("lines"):
                x0 = b["bbox"][0]  # left edge
                left_margins.append(round(x0, 1))
    doc.close()

    if not left_margins:
        return False
    margin_variance = max(left_margins) - min(left_margins)
    return margin_variance > 15  # threshold (points)


def detect_spelling_mistakes(text, max_chars=5000):
    """Detect spelling mistakes in the extracted text using pyspellchecker."""
    if not text:
        logger.warning("No text provided for spelling check")
        return {
            "total_errors": 0,
            "spelling_errors_count": 0,
            "spelling_errors": [],
            "characters_checked": 0,
        }

    logger.info(f"Starting spelling check on text (length: {len(text)})")
    logger.debug(f"Text preview for spell check (first 300 chars): {text[:300]}")

    spell = SpellChecker()

    # Limit text length for performance
    text_to_check = text[:max_chars]
    logger.info(f"Checking {len(text_to_check)} characters for spelling errors")

    words = re.findall(r"\b[a-zA-Z]+\b", text_to_check)
    logger.info(f"Extracted {len(words)} words for spell checking")
    logger.debug(f"Words extracted: {words[:50]}...")  # Log first 50 words

    # Find misspelled words
    misspelled = spell.unknown(words)
    logger.info(f"Found {len(misspelled)} misspelled words")
    logger.debug(f"Misspelled words: {list(misspelled)}")

    # Build error details
    spelling_errors = []
    for word in list(misspelled)[:10]:  # Limit to first 10 errors
        suggestions = spell.candidates(word)
        spelling_errors.append(
            {
                "word": word,
                "message": f"Possible spelling mistake: '{word}'",
                "replacements": list(suggestions)[:3] if suggestions else [],
            }
        )

    result = {
        "total_errors": len(misspelled),
        "spelling_errors_count": len(misspelled),
        "spelling_errors": spelling_errors,
        "characters_checked": len(text_to_check),
    }
    logger.info(f"Spelling check complete: {result['total_errors']} errors found")

    return result


def run_format_validation(text, file_path=None):
    """
    Run all formatting checks using extracted text.

    Args:
        text: The extracted text from the document
        file_path: Optional path to PDF file (only needed for font/indentation checks)

    Returns:
        Dictionary with validation results
    """
    results = {}

    # Text-based checks (work with any document type)
    results["double_spacing_occurrences"] = detect_double_spacing(text)
    results["spelling_mistakes"] = detect_spelling_mistakes(text)

    # PDF-specific checks (require direct PDF access)
    if (
        file_path
        and os.path.splitext(file_path)[-1].lower() == ".pdf"
        and os.path.exists(file_path)
    ):
        font_report = detect_irregular_fonts(file_path)
        results["irregular_fonts"] = (
            font_report["unique_fonts"] if font_report["unique_font_count"] > 1 else []
        )
        results["font_size_variants"] = font_report["font_size_variants"]
        results["indentation_inconsistent"] = detect_indentation_issues(file_path)
    else:
        results["note"] = (
            "Font and indentation checks only available for PDF files with file path provided."
        )

    return results
