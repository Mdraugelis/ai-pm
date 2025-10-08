# Dockerfile for AI Product Manager Agent
# Multi-stage build for production optimization

# ============================================================================
# Stage 1: Base
# ============================================================================
FROM python:3.11-slim as base

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 agent && chown -R agent:agent /app

# ============================================================================
# Stage 2: Dependencies
# ============================================================================
FROM base as dependencies

# Copy requirements
COPY requirements.txt requirements-dev.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ============================================================================
# Stage 3: Development
# ============================================================================
FROM dependencies as development

# Install development dependencies
RUN pip install --no-cache-dir -r requirements-dev.txt

# Copy application code
COPY --chown=agent:agent . .

# Switch to non-root user
USER agent

# Development command (will be overridden by docker-compose)
CMD ["python", "src/main.py", "--interactive"]

# ============================================================================
# Stage 4: Production
# ============================================================================
FROM dependencies as production

# Copy only necessary files
COPY --chown=agent:agent src/ ./src/
COPY --chown=agent:agent docs/ ./docs/
COPY --chown=agent:agent config/ ./config/
COPY --chown=agent:agent pyproject.toml ./

# Create logs directory
RUN mkdir -p logs && chown agent:agent logs

# Switch to non-root user
USER agent

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Production command
CMD ["python", "src/main.py"]

# ============================================================================
# Default target
# ============================================================================
FROM development
