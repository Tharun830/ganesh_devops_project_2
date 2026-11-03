# ==============================================================================
# Ganesh DevOps Project 2 - Full-Stack FastAPI Production Dockerfile
# Optimized multi-stage build with non-root security compliance
# ==============================================================================

FROM python:3.11-slim AS base

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_HOME=/app \
    PORT=8000

WORKDIR ${APP_HOME}

# Install curl for container healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies in cached layer
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY app/ ./app/

# Create a non-privileged user and group for security
RUN groupadd -r devops && useradd -r -g devops -d ${APP_HOME} appuser \
    && chown -R appuser:devops ${APP_HOME}

# Switch to non-root user
USER appuser

# Expose web application port
EXPOSE 8000

# Docker native container healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Production ASGI server execution via Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
