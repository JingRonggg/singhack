import logging


def setup_logging():
    """Configure logging for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()],
    )

    # Set specific module log levels
    logging.getLogger("backend.tools.document_extractor").setLevel(logging.DEBUG)
    logging.getLogger("backend.tools.format_validator").setLevel(logging.DEBUG)
