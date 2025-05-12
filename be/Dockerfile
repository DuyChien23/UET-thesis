FROM python:3.11-slim as requirements-stage

WORKDIR /tmp

COPY ./requirements.txt /tmp/

RUN pip wheel --no-cache-dir --no-deps --wheel-dir /tmp/wheels -r requirements.txt


FROM python:3.11-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user
RUN useradd -m -s /bin/bash app-user

# Copy Python dependencies from the first stage
COPY --from=requirements-stage /tmp/wheels /wheels
COPY --from=requirements-stage /tmp/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt \
    && rm -rf /wheels

# Copy application code
COPY . /app/

# Set proper permissions
RUN chown -R app-user:app-user /app

# Switch to non-root user
USER app-user

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ENVIRONMENT=production

# Set up the application
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Start the application with Uvicorn
CMD ["uvicorn", "src.api.app:app", "--host", "0.0.0.0", "--port", "8000"] 