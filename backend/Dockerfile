# Use uv's Alpine-based image
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Install system dependencies (poppler-utils and tesseract-ocr)
RUN apt-get update && apt-get install -y \
    poppler-utils \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /backend

# Copy dependency files first for better layer caching
COPY pyproject.toml ./

# Install Python dependencies using uv
RUN uv sync

# Copy the rest of the application
COPY . .

# Create necessary directories
RUN mkdir -p data/uploads

# Expose the port FastAPI runs on
EXPOSE 8000

# Set environment variables for poppler and tesseract paths
ENV PATH="/usr/bin:${PATH}"

# Run the FastAPI application with uv
CMD ["uv", "run", "fastapi", "dev", "main.py"]
