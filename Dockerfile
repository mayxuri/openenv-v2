# ── Customer Support OpenEnv ────────────────────────────────────────────────
# Runs the FastAPI environment server on port 7860 (Hugging Face Spaces default)
# Build:   docker build -t customer-support-env .
# Run:     docker run -p 7860:7860 customer-support-env
# ---------------------------------------------------------------------------
FROM python:3.11-slim

# Non-root user required by Hugging Face Spaces
RUN useradd -m -u 1000 appuser

WORKDIR /app

# Install dependencies first (layer cache)
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY --chown=appuser:appuser . .

USER appuser

EXPOSE 7860

# Start the environment server
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860", "--workers", "1"]
