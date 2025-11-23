# ============================================
# DOCKERFILE - FASTAPI MICROSERVICE
# ============================================
# Multi-stage build for optimized production images
# Follows Twelve-Factor App principles

# ============================================
# STAGE 1: Base Python Image
# ============================================
FROM python:3.12-slim as base

# Set environment variables (Factor III: Config)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Create app user (security best practice)
RUN useradd -m -u 1000 appuser

WORKDIR /app

# ============================================
# STAGE 2: Dependencies
# ============================================
FROM base as dependencies

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    default-libmysqlclient-dev \
    pkg-config \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --default-timeout=100 --retries=5 -r requirements.txt

# ============================================
# STAGE 3: Production
# ============================================
FROM base as production

# Copy installed packages from dependencies stage
COPY --from=dependencies /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

# Install minimal runtime dependencies
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy application code
COPY --chown=appuser:appuser . .

# Switch to non-root user (security)
USER appuser

# Expose port (Factor VII: Port binding)
EXPOSE 8003

# Health check (Factor IX: Disposability)
HEALTHCHECK --interval=10s --timeout=5s --retries=3 \
    CMD curl -f http://localhost:8003/health || exit 1

# Start command (Factor VI: Stateless processes)
CMD ["uvicorn", "main:app", \
     "--host", "0.0.0.0", \
     "--port", "8003", \
     "--workers", "1", \
     "--loop", "uvloop", \
     "--no-access-log", \
     "--log-level", "warning"]

# ============================================
# STAGE 4: Development (Optional)
# ============================================
FROM dependencies as development

# Install development tools
RUN pip install --no-cache-dir \
    black \
    isort \
    flake8 \
    pytest \
    pytest-cov

# Copy application code
COPY . .

# Development server with hot reload
CMD ["uvicorn", "main:app", \
     "--host", "0.0.0.0", \
     "--port", "8003", \
     "--reload", \
     "--log-level", "debug"]

