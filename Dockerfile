# ── Stage 1: builder ──────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /app

# Install dependencies into an isolated prefix so the final image stays lean
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ── Stage 2: runtime ──────────────────────────────────────────────────────────
FROM python:3.12-slim

# Security: run as non-root user
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

WORKDIR /app

# Copy installed packages from builder stage
COPY --from=builder /install /usr/local

# Copy application source
COPY app.py .
COPY test_app.py .

# Switch to non-root user
USER appuser

EXPOSE 5000

# Use gunicorn-style exec form; falls back to flask dev server for simplicity
CMD ["python", "app.py"]