# ── Base image ─────────────────────────────────────────────────
FROM python:3.12-slim

# ── System dependencies ─────────────────────────────────────────
# tesseract-ocr  : OCR engine for scanned PDF / image invoices
# tesseract-ocr-eng : English language data for Tesseract
# poppler-utils  : Provides pdfinfo / pdftoppm needed by pdf2image
# libglib2.0-0   : Required by some Pillow/image processing libs
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    poppler-utils \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Verify tesseract is accessible
RUN tesseract --version

# ── Working directory ───────────────────────────────────────────
WORKDIR /app

# ── Python dependencies ─────────────────────────────────────────
# Copy requirements first to leverage Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Application code ────────────────────────────────────────────
COPY . .

# ── Runtime ─────────────────────────────────────────────────────
# Railway injects the PORT environment variable automatically
EXPOSE 8080
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
