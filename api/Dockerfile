# Build stage
FROM python:3.11-slim AS builder

WORKDIR /app

# Install system dependencies needed for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && find /usr/local/lib/python3.11 -type d -name '__pycache__' -exec rm -rf {} + \
    && find /usr/local/lib/python3.11 -type f -name '*.pyc' -delete

# Runtime stage - use slim image for multi-arch support
FROM python:3.11-slim

WORKDIR /app

# Install runtime system dependencies (PostgreSQL client libraries)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libssl3 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Copy Python runtime and installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Copy application code
COPY app/ ./app/
COPY run.py .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Expose port
EXPOSE 5000

# Set Python path
ENV PYTHONPATH=/usr/local/lib/python3.11/site-packages
ENV PYTHONUNBUFFERED=1

# Run Python
ENTRYPOINT ["python3"]
CMD ["-u", "run.py"]
